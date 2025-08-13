from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from typing import Optional

from .config import settings
from .models.database import database_manager

redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    
    # Initialize Redis connection
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    
    # Initialize Prisma connection
    await database_manager.connect()
    
    yield
    
    # Cleanup
    if redis_client:
        await redis_client.close()
    await database_manager.disconnect()


app = FastAPI(
    title="Agent Engine Service",
    description="Multi-agent orchestration service for compliance analysis",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "environment": settings.ENVIRONMENT,
        "service_url": settings.SERVICE_URL
    }
    
    if redis_client:
        try:
            await redis_client.ping()
            health_status["redis"] = "connected"
        except Exception as e:
            health_status["redis"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    
    # Check Prisma/PostgreSQL connection
    try:
        if await database_manager.health_check():
            health_status["postgres"] = "connected"
        else:
            health_status["postgres"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["postgres"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "message": "Agent Engine Service is running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }