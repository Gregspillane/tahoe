"""
Transcription Service - Main Application Entry Point

Multi-provider transcription service with intelligent reconciliation
using AssemblyAI, OpenAI GPT-4o-transcribe, and GPT-5-mini.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import Settings
from middleware.authentication import get_current_user
from storage.file_discovery import FileDiscoveryService
from jobs.job_manager import JobManager
from workers.pool_manager import WorkerPoolManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global settings
settings = Settings()

# Global services (will be initialized in lifespan)
file_discovery_service = None
job_manager = None
worker_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global file_discovery_service, job_manager, worker_pool
    
    logger.info("Starting Transcription Service...")
    
    try:
        # Initialize core services
        logger.info("Initializing services...")
        
        # Initialize job manager (Redis connection)
        job_manager = JobManager(settings.redis_url)
        await job_manager.initialize()
        
        # Initialize worker pool
        worker_pool = WorkerPoolManager(
            job_manager=job_manager,
            worker_count=settings.worker_count
        )
        await worker_pool.start()
        
        # Initialize file discovery service
        file_discovery_service = FileDiscoveryService(
            job_manager=job_manager,
            poll_interval=settings.poll_interval
        )
        await file_discovery_service.start()
        
        logger.info("All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down services...")
        
        if file_discovery_service:
            await file_discovery_service.stop()
        
        if worker_pool:
            await worker_pool.stop()
        
        if job_manager:
            await job_manager.close()
        
        logger.info("Services shut down complete")


# Create FastAPI application
app = FastAPI(
    title="Transcription Service",
    description="Multi-provider transcription service with intelligent reconciliation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health and Status Endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "transcription"}


@app.get("/status")
async def service_status():
    """Detailed service status and metrics."""
    try:
        # Check Redis connection
        redis_status = "healthy" if job_manager and await job_manager.health_check() else "unhealthy"
        
        # Get queue statistics
        queue_stats = await job_manager.get_queue_stats() if job_manager else {}
        
        # Get worker status
        worker_status = worker_pool.get_status() if worker_pool else {}
        
        return {
            "status": "operational",
            "services": {
                "redis": redis_status,
                "workers": worker_status,
                "file_discovery": "running" if file_discovery_service else "stopped"
            },
            "queue": queue_stats,
            "settings": {
                "worker_count": settings.worker_count,
                "poll_interval": settings.poll_interval,
                "max_retries": settings.max_retries
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Service status check failed")


# Transcription Management Endpoints
@app.post("/transcribe/submit")
async def submit_transcription(
    audio_file_url: str,
    client_id: str = None,
    priority: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Submit audio file for transcription."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Create transcription job
        job_id = await job_manager.create_job(
            audio_file_url=audio_file_url,
            client_id=client_id,
            priority=priority
        )
        
        logger.info(f"Created transcription job {job_id} for {audio_file_url}")
        
        return {
            "job_id": job_id,
            "status": "submitted",
            "message": "Transcription job submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit transcription job: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit transcription job")


@app.get("/transcribe/status/{job_id}")
async def get_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get transcription job status."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        status = await job_manager.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/transcribe/result/{job_id}")
async def get_transcript(job_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve completed transcript."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        result = await job_manager.get_job_result(job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job or result not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transcript")


@app.post("/transcribe/bulk-status")
async def get_bulk_status(
    job_ids: list[str],
    current_user: dict = Depends(get_current_user)
):
    """Check multiple job statuses."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        statuses = await job_manager.get_bulk_status(job_ids)
        
        return {"statuses": statuses}
        
    except Exception as e:
        logger.error(f"Failed to get bulk status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bulk status")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    """Run the application directly for development."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )