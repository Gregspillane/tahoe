from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
import asyncpg
from typing import Optional

from .config import settings

redis_client: Optional[redis.Redis] = None
pg_pool: Optional[asyncpg.Pool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, pg_pool
    
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    
    pg_pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=1,
        max_size=10
    )
    
    yield
    
    if redis_client:
        await redis_client.close()
    if pg_pool:
        await pg_pool.close()


app = FastAPI(
    title="Agent Engine Service",
    description="Multi-agent orchestration service for compliance analysis",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": "agent-engine",
        "version": "0.1.0"
    }
    
    if redis_client:
        try:
            await redis_client.ping()
            health_status["redis"] = "connected"
        except Exception as e:
            health_status["redis"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    
    if pg_pool:
        try:
            async with pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["postgres"] = "connected"
        except Exception as e:
            health_status["postgres"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    return {
        "service": "agent-engine",
        "message": "Agent Engine Service is running",
        "docs": "/docs"
    }