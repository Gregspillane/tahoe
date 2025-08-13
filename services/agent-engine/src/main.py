from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from config import settings

# Import API routers
from .api.specifications import router as specifications_router
from .api.database import router as database_router
from .api.configuration import router as configuration_router
from .services.database import init_database

app = FastAPI(
    title=settings.agent_engine.title,
    description=settings.agent_engine.description,
    version=settings.agent_engine.version,
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routers
app.include_router(specifications_router, prefix="/api")
app.include_router(database_router, prefix="/api")
app.include_router(configuration_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    try:
        await init_database()
    except Exception as e:
        print(f"Failed to initialize database: {e}")

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": settings.agent_engine.name,
        "version": settings.agent_engine.version,
        "environment": settings.environment
    }

@app.get("/adk/verify")
async def verify_adk() -> Dict[str, Any]:
    """Verify ADK components are working correctly."""
    results = {
        "status": "verifying",
        "components": {}
    }
    
    # Test imports
    try:
        from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
        results["components"]["imports"] = "success"
        results["components"]["agent_types"] = ["LlmAgent", "SequentialAgent", "ParallelAgent", "LoopAgent", "BaseAgent"]
    except Exception as e:
        results["components"]["imports"] = f"failed: {str(e)}"
    
    # Test agent creation
    try:
        from google.adk.agents import LlmAgent
        agent = LlmAgent(
            name="verify",
            model="gemini-2.0-flash",
            instruction="Verification agent for testing ADK components"
        )
        results["components"]["agent_creation"] = "success"
        results["components"]["test_agent"] = {
            "name": agent.name,
            "model": agent.model
        }
    except Exception as e:
        results["components"]["agent_creation"] = f"failed: {str(e)}"
    
    # Test runner
    try:
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import LlmAgent
        
        if 'agent' not in locals():
            agent = LlmAgent(name="verify", model="gemini-2.0-flash", instruction="Test")
        
        runner = InMemoryRunner(agent, app_name="verify")
        results["components"]["runner"] = "success"
        results["components"]["runner_methods"] = {
            "has_run": hasattr(runner, 'run'),
            "has_run_async": hasattr(runner, 'run_async'),
            "has_session_service": hasattr(runner, 'session_service')
        }
    except Exception as e:
        results["components"]["runner"] = f"failed: {str(e)}"
    
    # Test session
    try:
        if 'runner' in locals():
            session_service = runner.session_service
            session = session_service.create_session(
                app_name="verify",
                user_id="test-user"
            )
            results["components"]["session"] = "success"
            results["components"]["session_info"] = {
                "session_id": str(session.id),
                "user_id": session.user_id,
                "app_name": session.app_name
            }
        else:
            results["components"]["session"] = "skipped: runner not available"
    except Exception as e:
        results["components"]["session"] = f"failed: {str(e)}"
    
    # Test tools
    try:
        from google.adk.tools import FunctionTool, google_search
        
        def test_tool(x: int) -> int:
            return x * 2
        
        wrapped_tool = FunctionTool(test_tool)
        results["components"]["tools"] = "success"
        results["components"]["tool_features"] = {
            "function_tool": "available",
            "google_search": "available",
            "automatic_wrapping": "supported"
        }
    except Exception as e:
        results["components"]["tools"] = f"failed: {str(e)}"
    
    # Overall status
    all_success = all(
        v == "success" 
        for k, v in results["components"].items() 
        if isinstance(v, str) and k in ["imports", "agent_creation", "runner", "session", "tools"]
    )
    
    results["status"] = "verified" if all_success else "partial"
    results["all_components_operational"] = all_success
    
    # Add configuration info
    results["configuration"] = {
        "environment": settings.environment,
        "adk_model": settings.adk.default_model,
        "service_name": settings.agent_engine.name
    }
    
    return results


@app.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """Get current configuration (for debugging/monitoring)."""
    return {
        "environment": settings.environment,
        "service": {
            "name": settings.agent_engine.name,
            "version": settings.agent_engine.version,
            "host": settings.agent_engine.host,
            "port": settings.agent_engine.port
        },
        "adk": {
            "default_model": settings.adk.default_model,
            "max_retries": settings.adk.max_retries,
            "timeout": settings.adk.timeout
        },
        "database": {
            "host": settings.database.host,
            "port": settings.database.port,
            "name": settings.database.name
        },
        "redis": {
            "host": settings.redis.host,
            "port": settings.redis.port,
            "db": settings.redis.db
        }
    }