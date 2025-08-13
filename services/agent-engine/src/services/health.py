"""Health check service for agent-engine"""

from typing import Dict
from datetime import datetime
import redis.asyncio as redis
from prisma import Prisma
import os


class HealthChecker:
    """Service health checker with dependency validation"""
    
    def __init__(self):
        self.service_name = "agent-engine"
        self.version = os.getenv("SERVICE_VERSION", "1.0.0")
        
    async def check_postgres(self) -> Dict[str, str]:
        """Check PostgreSQL connectivity"""
        try:
            db = Prisma()
            await db.connect()
            # Simple query to verify connection
            await db.agenttemplate.count()
            await db.disconnect()
            return {"postgres": "healthy"}
        except Exception as e:
            return {"postgres": f"unhealthy: {str(e)}"}
    
    async def check_redis(self) -> Dict[str, str]:
        """Check Redis connectivity"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6382")
            cache = redis.from_url(redis_url, decode_responses=True)
            await cache.ping()
            await cache.close()
            return {"redis": "healthy"}
        except Exception as e:
            return {"redis": f"unhealthy: {str(e)}"}
    
    async def check_all(self) -> Dict[str, any]:
        """
        Check all service dependencies
        
        Returns:
            Dictionary with overall health status and dependency details
        """
        dependencies = {}
        
        # Check PostgreSQL
        postgres_status = await self.check_postgres()
        dependencies.update(postgres_status)
        
        # Check Redis
        redis_status = await self.check_redis()
        dependencies.update(redis_status)
        
        # Determine overall status
        all_healthy = all(
            "healthy" in status 
            for status in dependencies.values()
        )
        
        return {
            "service": self.service_name,
            "status": "healthy" if all_healthy else "degraded",
            "version": self.version,
            "dependencies": dependencies,
            "timestamp": datetime.now().isoformat()
        }


class MetricsCollector:
    """Basic metrics collection for service monitoring"""
    
    def __init__(self):
        self.requests_total = 0
        self.errors_total = 0
        self.analysis_requests = []
        self.last_reset = datetime.now()
        
    def inc_requests(self):
        """Increment total request counter"""
        self.requests_total += 1
        
    def inc_errors(self):
        """Increment error counter"""
        self.errors_total += 1
        
    def record_analysis(self, duration: float):
        """Record an analysis request duration"""
        self.analysis_requests.append({
            "timestamp": datetime.now().isoformat(),
            "duration": duration
        })
        # Keep only last 100 requests
        if len(self.analysis_requests) > 100:
            self.analysis_requests = self.analysis_requests[-100:]
    
    async def get_current_metrics(self) -> Dict[str, any]:
        """Get current metrics snapshot"""
        now = datetime.now()
        uptime_seconds = (now - self.last_reset).total_seconds()
        
        # Calculate averages
        avg_response_time = 0.0
        if self.analysis_requests:
            avg_response_time = sum(
                r["duration"] for r in self.analysis_requests
            ) / len(self.analysis_requests)
        
        # Get active analyses from Redis
        active_analyses = 0
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6382")
            cache = redis.from_url(redis_url, decode_responses=True)
            keys = await cache.keys("analysis:session:*")
            active_analyses = len(keys)
            await cache.close()
        except:
            pass
        
        return {
            "requests_total": self.requests_total,
            "requests_per_minute": (self.requests_total / uptime_seconds) * 60 if uptime_seconds > 0 else 0,
            "average_response_time": avg_response_time,
            "active_analyses": active_analyses,
            "cache_hit_rate": 0.0,  # Placeholder for now
            "errors_total": self.errors_total,
            "uptime_seconds": uptime_seconds,
            "timestamp": now.isoformat()
        }