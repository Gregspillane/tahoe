"""Main FastAPI application for agent-engine service"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime
import logging
import json

from .config import settings
from .models.database import database_manager
from .models.api import (
    AnalysisRequest, AnalysisResponse, AnalysisStatus,
    AgentTemplateCreate, AgentTemplateUpdate, 
    ScorecardCreate, HealthStatus, MetricsResponse,
    AuthContext
)
from .auth import verify_service_token
from .orchestrator import TahoeOrchestrator
from .services.health import HealthChecker, MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
orchestrator: Optional[TahoeOrchestrator] = None
health_checker: Optional[HealthChecker] = None
metrics: Optional[MetricsCollector] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator, health_checker, metrics
    
    logger.info(f"Starting {settings.SERVICE_NAME} service")
    
    # Initialize services
    orchestrator = TahoeOrchestrator()
    await orchestrator.initialize()
    
    health_checker = HealthChecker()
    metrics = MetricsCollector()
    
    # Initialize database connection
    await database_manager.connect()
    
    # Warm up caches
    try:
        cache_count = await orchestrator.warmup_caches()
        logger.info(f"Warmed up cache with {cache_count} agent templates")
    except Exception as e:
        logger.warning(f"Cache warmup failed: {str(e)}")
    
    logger.info(f"{settings.SERVICE_NAME} service started successfully")
    
    yield
    
    # Cleanup
    logger.info(f"Shutting down {settings.SERVICE_NAME} service")
    
    if orchestrator:
        await orchestrator.cleanup()
    
    await database_manager.disconnect()
    
    logger.info(f"{settings.SERVICE_NAME} service shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="Multi-agent orchestration for compliance analysis",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Root endpoint
@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "message": f"{settings.SERVICE_NAME} is running",
        "docs": "/docs",
        "health": "/health"
    }


# Health and Monitoring Endpoints
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Service health check with dependency validation"""
    health_status = await health_checker.check_all()
    
    if health_status["status"] != "healthy":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Service operational metrics"""
    try:
        return await metrics.get_current_metrics()
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Core Analysis Endpoints
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_interaction(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(verify_service_token)
):
    """Submit interaction for multi-agent analysis"""
    
    try:
        # Track metrics
        start_time = datetime.now()
        metrics.inc_requests()
        
        logger.info(f"Starting analysis for interaction {request.interaction.id}")
        
        # Execute analysis (skeleton for now)
        result = await orchestrator.analyze_interaction(
            request.interaction.model_dump(),
            request.scorecard_id,
            request.portfolio_id,
            request.options
        )
        
        # Track execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        metrics.record_analysis(execution_time)
        
        # Return structured response
        response = AnalysisResponse(
            analysis_id=result.analysis_id,
            status="complete",
            overall_score=result.overall_score,
            confidence=result.confidence,
            categories=result.categories,
            violations=result.violations,
            recommendations=result.recommendations,
            audit_trail=result.audit_trail,
            execution_time=execution_time
        )
        
        logger.info(f"Analysis completed for {request.interaction.id}: score={result.overall_score}")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.interaction.id}: {str(e)}")
        metrics.inc_errors()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    auth: AuthContext = Depends(verify_service_token)
):
    """Retrieve analysis results by ID"""
    
    try:
        db = database_manager.get_client()
        analysis = await db.analysis.find_unique({
            "where": {"id": analysis_id}
        })
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisResponse(
            analysis_id=analysis.id,
            status=analysis.status,
            overall_score=analysis.overallScore,
            confidence=analysis.confidence,
            categories=analysis.results if analysis.results else {},
            violations=analysis.violations if analysis.violations else [],
            recommendations=analysis.recommendations if analysis.recommendations else [],
            audit_trail={
                "trace_id": analysis.traceId,
                "execution_time": analysis.executionTime,
                "created_at": analysis.createdAt.isoformat(),
                "completed_at": analysis.completedAt.isoformat() if analysis.completedAt else None
            },
            execution_time=analysis.executionTime
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/analysis/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(
    analysis_id: str,
    auth: AuthContext = Depends(verify_service_token)
):
    """Get real-time analysis status"""
    
    try:
        status_data = await orchestrator.get_analysis_status(analysis_id)
        
        if not status_data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisStatus(
            analysis_id=analysis_id,
            status=status_data.get("status", "unknown"),
            phase=status_data.get("phase"),
            started_at=status_data.get("started_at"),
            completed_at=status_data.get("completed_at"),
            trace_id=status_data.get("trace_id")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent Template Management Endpoints
@app.get("/agents/templates")
async def list_agent_templates(
    active_only: bool = True,
    auth: AuthContext = Depends(verify_service_token)
):
    """List available agent templates"""
    
    try:
        db = database_manager.get_client()
        
        where_clause = {"isActive": True} if active_only else {}
        
        templates = await db.agenttemplate.find_many({
            "where": where_clause,
            "order_by": {"name": "asc"}
        })
        
        return templates
        
    except Exception as e:
        logger.error(f"Failed to list agent templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/templates")
async def create_agent_template(
    template: AgentTemplateCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new agent template"""
    
    try:
        db = database_manager.get_client()
        
        # Convert Pydantic model to dict for Prisma
        template_data = template.model_dump()
        
        agent = await db.agenttemplate.create({
            "data": template_data
        })
        
        logger.info(f"Created agent template: {agent.name}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/agents/templates/{template_id}")
async def update_agent_template(
    template_id: str,
    updates: AgentTemplateUpdate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Update agent template"""
    
    try:
        db = database_manager.get_client()
        
        # Get current version
        current = await db.agenttemplate.find_unique({
            "where": {"id": template_id}
        })
        
        if not current:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Prepare update data
        update_data = updates.model_dump(exclude_unset=True)
        update_data["version"] = current.version + 1
        update_data["updatedAt"] = datetime.now()
        
        # Update with version increment
        agent = await db.agenttemplate.update({
            "where": {"id": template_id},
            "data": update_data
        })
        
        # Invalidate cache
        if orchestrator and orchestrator.cache:
            await orchestrator.cache.delete(f"agent:template:{template_id}")
        
        logger.info(f"Updated agent template {template_id} to version {agent.version}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Scorecard Management Endpoints
@app.get("/scorecards")
async def list_scorecards(
    portfolio_id: Optional[str] = None,
    active_only: bool = True,
    auth: AuthContext = Depends(verify_service_token)
):
    """List available scorecards"""
    
    try:
        db = database_manager.get_client()
        
        where_clause = {}
        if portfolio_id:
            where_clause["portfolioId"] = portfolio_id
        if active_only:
            where_clause["isActive"] = True
        
        scorecards = await db.scorecard.find_many({
            "where": where_clause,
            "include": {
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            },
            "order_by": {"name": "asc"}
        })
        
        return scorecards
        
    except Exception as e:
        logger.error(f"Failed to list scorecards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scorecards")
async def create_scorecard(
    scorecard: ScorecardCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new scorecard configuration"""
    
    try:
        db = database_manager.get_client()
        
        # Convert Pydantic model to dict for Prisma
        scorecard_data = scorecard.model_dump()
        
        result = await db.scorecard.create({
            "data": scorecard_data
        })
        
        logger.info(f"Created scorecard: {result.name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create scorecard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Error Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)