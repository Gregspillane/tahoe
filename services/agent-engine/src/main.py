from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging
from config import settings

# Import API routers
from .api.specifications import router as specifications_router
from .api.database import router as database_router
from .api.configuration import router as configuration_router
from .services.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.environment != "production" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.agent_engine.title,
    description=settings.agent_engine.description,
    version=settings.agent_engine.version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(specifications_router, prefix="/api")
app.include_router(database_router, prefix="/api")
app.include_router(configuration_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup."""
    logger.info("Starting agent-engine service...")

    # Initialize database connection
    try:
        db = get_db()
        await db.connect()
        logger.info("Database connection established successfully")

        # Perform health check
        health = await db.health_check()
        logger.info(f"Database health check: {health}")

        # Log initial statistics
        stats = await db.get_statistics()
        logger.info(
            f"Database statistics: Sessions={stats['sessions']}, Executions={stats['executions']}"
        )

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # In production, you might want to fail fast here
        if settings.environment == "production":
            raise
        else:
            logger.warning("Running without database connection in development mode")

    logger.info(
        f"Agent-engine service started successfully in {settings.environment} mode"
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    logger.info("Shutting down agent-engine service...")

    # Disconnect database
    try:
        db = get_db()
        if db._connected:
            # Log final statistics before shutdown
            stats = await db.get_statistics()
            logger.info(
                f"Final statistics: Sessions={stats['sessions']}, Executions={stats['executions']}"
            )

            # Gracefully disconnect
            await db.disconnect()
            logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error during database shutdown: {e}")

    logger.info("Agent-engine service shutdown complete")


@app.get("/health")
async def health():
    """Health check endpoint with database status."""
    health_status = {
        "status": "healthy",
        "service": settings.agent_engine.name,
        "version": settings.agent_engine.version,
        "environment": settings.environment,
        "database": {"status": "unknown"},
    }

    # Check database health
    try:
        db = get_db()
        db_health = await db.health_check()
        health_status["database"] = db_health

        # Overall health is unhealthy if database is unhealthy
        if db_health.get("status") != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["database"] = {"status": "error", "error": str(e)}
        health_status["status"] = "degraded"

    return health_status


@app.get("/adk/verify")
async def verify_adk() -> Dict[str, Any]:
    """Verify ADK components are working correctly."""
    results = {"status": "verifying", "components": {}}

    # Test imports
    try:
        from google.adk.agents import LlmAgent

        results["components"]["imports"] = "success"
        results["components"]["agent_types"] = [
            "LlmAgent",
            "SequentialAgent",
            "ParallelAgent",
            "LoopAgent",
            "BaseAgent",
        ]
    except Exception as e:
        results["components"]["imports"] = f"failed: {str(e)}"

    # Test agent creation
    try:
        from google.adk.agents import LlmAgent

        agent = LlmAgent(
            name="verify",
            model="gemini-2.0-flash",
            instruction="Verification agent for testing ADK components",
        )
        results["components"]["agent_creation"] = "success"
        results["components"]["test_agent"] = {"name": agent.name, "model": agent.model}
    except Exception as e:
        results["components"]["agent_creation"] = f"failed: {str(e)}"

    # Test runner
    try:
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import LlmAgent

        if "agent" not in locals():
            agent = LlmAgent(
                name="verify", model="gemini-2.0-flash", instruction="Test"
            )

        runner = InMemoryRunner(agent, app_name="verify")
        results["components"]["runner"] = "success"
        results["components"]["runner_methods"] = {
            "has_run": hasattr(runner, "run"),
            "has_run_async": hasattr(runner, "run_async"),
            "has_session_service": hasattr(runner, "session_service"),
        }
    except Exception as e:
        results["components"]["runner"] = f"failed: {str(e)}"

    # Test session
    try:
        if "runner" in locals():
            session_service = runner.session_service
            # Check if create_session is async
            import inspect

            if inspect.iscoroutinefunction(session_service.create_session):
                # Handle async session creation - use await since we're in async context
                session = await session_service.create_session(
                    app_name="verify", user_id="test-user"
                )
            else:
                # Handle sync session creation
                session = session_service.create_session(
                    app_name="verify", user_id="test-user"
                )

            results["components"]["session"] = "success"
            results["components"]["session_info"] = {
                "session_id": str(session.id),
                "user_id": session.user_id,
                "app_name": session.app_name,
            }
        else:
            results["components"]["session"] = "skipped: runner not available"
    except Exception as e:
        results["components"]["session"] = f"failed: {str(e)}"

    # Test tools
    try:
        from google.adk.tools import FunctionTool

        def test_tool(x: int) -> int:
            return x * 2

        wrapped_tool = FunctionTool(test_tool)
        results["components"]["tools"] = "success"
        results["components"]["tool_features"] = {
            "function_tool": "available",
            "google_search": "available",
            "automatic_wrapping": "supported",
        }
    except Exception as e:
        results["components"]["tools"] = f"failed: {str(e)}"

    # Overall status
    all_success = all(
        v == "success"
        for k, v in results["components"].items()
        if isinstance(v, str)
        and k in ["imports", "agent_creation", "runner", "session", "tools"]
    )

    results["status"] = "verified" if all_success else "partial"
    results["all_components_operational"] = all_success

    # Add configuration info
    results["configuration"] = {
        "environment": settings.environment,
        "adk_model": settings.adk.default_model,
        "service_name": settings.agent_engine.name,
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
            "port": settings.agent_engine.port,
        },
        "adk": {
            "default_model": settings.adk.default_model,
            "max_retries": settings.adk.max_retries,
            "timeout": settings.adk.timeout,
        },
        "database": {
            "host": settings.database.host,
            "port": settings.database.port,
            "name": settings.database.name,
        },
        "redis": {
            "host": settings.redis.host,
            "port": settings.redis.port,
            "db": settings.redis.db,
        },
    }
