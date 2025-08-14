"""
Redis/Bull queue job management for the Transcription Service.
"""

import asyncio
import logging
import json
from typing import Optional, Dict, List
import redis.asyncio as redis
from datetime import datetime

logger = logging.getLogger(__name__)


class JobManager:
    """Manages transcription jobs using Redis as the backend."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
    
    async def create_job(self, audio_file_url: str, client_id: str = None, priority: int = 0) -> str:
        """Create a new transcription job."""
        # For MVP, return a mock job ID
        # In full implementation, create job in database and queue
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(audio_file_url) % 10000}"
        
        job_data = {
            "job_id": job_id,
            "audio_file_url": audio_file_url,
            "client_id": client_id,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Store job in Redis for now
        await self.redis_client.hset(f"job:{job_id}", mapping=job_data)
        
        logger.info(f"Created job {job_id}")
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status."""
        try:
            job_data = await self.redis_client.hgetall(f"job:{job_id}")
            if job_data:
                return {k.decode(): v.decode() for k, v in job_data.items()}
            return None
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    async def get_job_result(self, job_id: str) -> Optional[Dict]:
        """Get job result."""
        job_status = await self.get_job_status(job_id)
        if not job_status:
            return None
        
        # For MVP, return mock result
        return {
            "job_id": job_id,
            "status": job_status.get("status", "pending"),
            "transcript_url": f"s3://transcripts/{job_id}/final.md" if job_status.get("status") == "completed" else None
        }
    
    async def get_bulk_status(self, job_ids: List[str]) -> List[Dict]:
        """Get status for multiple jobs."""
        statuses = []
        for job_id in job_ids:
            status = await self.get_job_status(job_id)
            statuses.append(status or {"job_id": job_id, "status": "not_found"})
        return statuses
    
    async def get_queue_stats(self) -> Dict:
        """Get queue statistics."""
        # For MVP, return mock stats
        return {
            "pending_jobs": 0,
            "processing_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0
        }