"""
Tahoe API Server - Main FastAPI application
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Optional
import os

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from ..core.agent_factory import AgentFactory
from ..core.config_loader import ConfigLoader
from .models import (
    AgentCreateRequest, AgentExecuteRequest, AgentResponse,
    SessionCreateRequest, SessionResponse, ErrorResponse
)
from .middleware.auth import verify_service_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
agent_factory: Optional[AgentFactory] = None
config_loader: Optional[ConfigLoader] = None
session_service: Optional[InMemorySessionService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent_factory, config_loader, session_service
    
    # Initialize services
    logger.info("Initializing Tahoe services...")
    agent_factory = AgentFactory()
    config_loader = ConfigLoader()
    session_service = InMemorySessionService()
    
    logger.info("Tahoe API server started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Tahoe services...")


# Create FastAPI app
app = FastAPI(
    title="Tahoe Agent Orchestration Service",
    description="Universal agent orchestration API built on Google ADK",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Tahoe Agent Orchestration",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/agents", response_model=dict, dependencies=[Depends(verify_service_token)])
async def create_agent(request: AgentCreateRequest):
    """
    Create a new agent from configuration
    """
    try:
        # Load template if specified
        if request.template:
            base_config = config_loader.load_template(request.template)
            config = config_loader.merge_configs(base_config, {
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            })
        else:
            config = {
                "name": request.name,
                "type": request.type,
                "description": request.description,
                "config": request.config
            }
        
        # Validate configuration
        config_loader.validate_config(config)
        
        # Create agent
        agent = agent_factory.create_agent(config)
        
        return {
            "agent_id": request.name,
            "status": "created",
            "type": request.type
        }
        
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/agents/{agent_id}/execute", response_model=AgentResponse, dependencies=[Depends(verify_service_token)])
async def execute_agent(agent_id: str, request: AgentExecuteRequest):
    """
    Execute an agent with the given input
    """
    try:
        # Get agent
        agent = agent_factory.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
        
        # Create or get session
        if request.session_id:
            session = await session_service.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session not found: {request.session_id}")
        else:
            # Create new session
            session = await session_service.create_session(
                app_name="tahoe",
                user_id=request.context.get("user_id", "default")
            )
        
        # Create runner
        runner = Runner(
            agent=agent,
            app_name="tahoe",
            session_service=session_service
        )
        
        # Execute agent
        events = []
        async for event in runner.run_async(
            new_message=request.input,
            session=session
        ):
            events.append(event)
        
        # Extract final response
        final_response = ""
        if events:
            last_event = events[-1]
            if last_event.content and last_event.content.parts:
                final_response = last_event.content.parts[0].text or ""
        
        return AgentResponse(
            agent_id=agent_id,
            session_id=session.id,
            response=final_response,
            state=session.state,
            metadata={
                "event_count": len(events)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions", response_model=SessionResponse, dependencies=[Depends(verify_service_token)])
async def create_session(request: SessionCreateRequest):
    """
    Create a new session
    """
    try:
        session = await session_service.create_session(
            app_name="tahoe",
            user_id=request.user_id
        )
        
        # Set initial state if provided
        if request.initial_state:
            session.state.update(request.initial_state)
        
        return SessionResponse(
            session_id=session.id,
            user_id=request.user_id,
            agent_id=request.agent_id,
            state=session.state,
            created_at=str(session.created_at),
            last_updated=str(session.last_updated)
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionResponse, dependencies=[Depends(verify_service_token)])
async def get_session(session_id: str):
    """
    Get session information
    """
    try:
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        
        return SessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            agent_id="",  # Would need to track this separately
            state=session.state,
            created_at=str(session.created_at),
            last_updated=str(session.last_updated)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)