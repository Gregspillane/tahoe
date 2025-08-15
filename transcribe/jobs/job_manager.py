"""
Redis queue job management for the Transcription Service.
Implements proper queue functionality with job persistence and worker claiming.
"""

import asyncio
import logging
import json
import uuid
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class JobManager:
    """Manages transcription jobs using Redis as the backend with proper queue functionality."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        
        # Queue names
        self.pending_queue = "transcription:queue:pending"
        self.processing_queue = "transcription:queue:processing"
        self.completed_queue = "transcription:queue:completed"
        self.failed_queue = "transcription:queue:failed"
        
        # Job data keys
        self.job_prefix = "transcription:job:"
        self.worker_prefix = "transcription:worker:"
        
        # Settings
        self.job_timeout = 30 * 60  # 30 minutes default timeout
        self.retry_delay = 60  # 1 minute retry delay
        self.max_retries = 3
        
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("JobManager connected to Redis successfully")
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
        """Create a new transcription job and add it to the pending queue."""
        job_id = str(uuid.uuid4())
        
        job_data = {
            "job_id": job_id,
            "audio_file_url": audio_file_url,
            "client_id": client_id or "default",
            "priority": str(priority),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "retry_count": "0",
            "max_retries": str(self.max_retries),
            "worker_id": "",
            "started_at": "",
            "completed_at": "",
            "error_message": ""
        }
        
        # Use Redis transaction to ensure atomicity
        async with self.redis_client.pipeline() as pipe:
            # Store job data
            await pipe.hset(f"{self.job_prefix}{job_id}", mapping=job_data)
            
            # Add to pending queue with priority (higher number = higher priority)
            await pipe.zadd(self.pending_queue, {job_id: priority})
            
            # Execute transaction
            await pipe.execute()
        
        logger.info(f"Created job {job_id} for audio file: {audio_file_url}")
        return job_id
    
    async def claim_job(self, worker_id: str) -> Optional[Dict]:
        """Claim a job from the pending queue for processing."""
        try:
            # Get highest priority job from pending queue
            result = await self.redis_client.zpopmax(self.pending_queue)
            
            if not result:
                return None
            
            job_id, priority = result[0]
            job_id = job_id.decode() if isinstance(job_id, bytes) else job_id
            
            # Get job data
            job_data = await self.redis_client.hgetall(f"{self.job_prefix}{job_id}")
            if not job_data:
                logger.warning(f"Job {job_id} data not found when claiming")
                return None
            
            # Convert bytes to strings
            job_data = {k.decode(): v.decode() for k, v in job_data.items()}
            
            # Update job status and assign worker
            update_data = {
                "status": "processing",
                "worker_id": worker_id,
                "started_at": datetime.now().isoformat()
            }
            
            # Use transaction to update job and add to processing queue
            async with self.redis_client.pipeline() as pipe:
                await pipe.hset(f"{self.job_prefix}{job_id}", mapping=update_data)
                await pipe.zadd(self.processing_queue, {job_id: datetime.now().timestamp()})
                await pipe.execute()
            
            # Merge update data with job data
            job_data.update(update_data)
            
            logger.info(f"Worker {worker_id} claimed job {job_id}")
            return job_data
            
        except Exception as e:
            logger.error(f"Failed to claim job: {e}")
            return None
    
    async def complete_job(self, job_id: str, transcript_url: str = None, error_message: str = None, result_data: Dict = None):
        """Mark a job as completed or failed."""
        try:
            if error_message:
                # Handle job failure
                await self._handle_job_failure(job_id, error_message)
            else:
                # Handle job success
                update_data = {
                    "status": "completed",
                    "completed_at": datetime.now().isoformat(),
                    "transcript_url": transcript_url or "",
                    "worker_id": ""
                }
                
                # Store result data if provided
                if result_data:
                    update_data["result_data"] = json.dumps(result_data)
                
                async with self.redis_client.pipeline() as pipe:
                    await pipe.hset(f"{self.job_prefix}{job_id}", mapping=update_data)
                    await pipe.zrem(self.processing_queue, job_id)
                    await pipe.zadd(self.completed_queue, {job_id: datetime.now().timestamp()})
                    await pipe.execute()
                
                logger.info(f"Job {job_id} completed successfully")
                
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
    
    async def _handle_job_failure(self, job_id: str, error_message: str):
        """Handle job failure with retry logic."""
        job_data = await self.redis_client.hgetall(f"{self.job_prefix}{job_id}")
        if not job_data:
            return
        
        job_data = {k.decode(): v.decode() for k, v in job_data.items()}
        retry_count = int(job_data.get("retry_count", 0))
        max_retries = int(job_data.get("max_retries", self.max_retries))
        
        if retry_count < max_retries:
            # Retry the job
            update_data = {
                "status": "pending",
                "retry_count": retry_count + 1,
                "error_message": error_message,
                "worker_id": "",
                "started_at": ""
            }
            
            async with self.redis_client.pipeline() as pipe:
                await pipe.hset(f"{self.job_prefix}{job_id}", mapping=update_data)
                await pipe.zrem(self.processing_queue, job_id)
                # Add back to pending with delay (using future timestamp)
                retry_time = datetime.now().timestamp() + self.retry_delay
                await pipe.zadd(self.pending_queue, {job_id: retry_time})
                await pipe.execute()
            
            logger.info(f"Job {job_id} failed, retry {retry_count + 1}/{max_retries}: {error_message}")
        else:
            # Max retries reached, mark as failed
            update_data = {
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error_message": error_message,
                "worker_id": ""
            }
            
            async with self.redis_client.pipeline() as pipe:
                await pipe.hset(f"{self.job_prefix}{job_id}", mapping=update_data)
                await pipe.zrem(self.processing_queue, job_id)
                await pipe.zadd(self.failed_queue, {job_id: datetime.now().timestamp()})
                await pipe.execute()
            
            logger.error(f"Job {job_id} permanently failed after {max_retries} retries: {error_message}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status and data."""
        try:
            job_data = await self.redis_client.hgetall(f"{self.job_prefix}{job_id}")
            if job_data:
                return {k.decode(): v.decode() for k, v in job_data.items()}
            return None
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    async def get_job_result(self, job_id: str) -> Optional[Dict]:
        """Get job result."""
        job_status = await self.get_job_status(job_id)
        if not job_status:
            return None
        
        result = {
            "job_id": job_id,
            "status": job_status.get("status", "pending"),
            "transcript_url": job_status.get("transcript_url") if job_status.get("status") == "completed" else None,
            "error_message": job_status.get("error_message") if job_status.get("status") == "failed" else None,
            "created_at": job_status.get("created_at"),
            "completed_at": job_status.get("completed_at")
        }
        
        # Include result data if available
        if job_status.get("result_data"):
            try:
                result["result_data"] = json.loads(job_status["result_data"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse result_data for job {job_id}")
        
        return result
    
    async def get_bulk_status(self, job_ids: List[str]) -> List[Dict]:
        """Get status for multiple jobs."""
        statuses = []
        for job_id in job_ids:
            status = await self.get_job_status(job_id)
            statuses.append(status or {"job_id": job_id, "status": "not_found"})
        return statuses
    
    async def get_queue_stats(self) -> Dict:
        """Get queue statistics."""
        try:
            pending_count = await self.redis_client.zcard(self.pending_queue)
            processing_count = await self.redis_client.zcard(self.processing_queue)
            completed_count = await self.redis_client.zcard(self.completed_queue)
            failed_count = await self.redis_client.zcard(self.failed_queue)
            
            return {
                "pending_jobs": pending_count,
                "processing_jobs": processing_count,
                "completed_jobs": completed_count,
                "failed_jobs": failed_count,
                "total_jobs": pending_count + processing_count + completed_count + failed_count
            }
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {
                "pending_jobs": 0,
                "processing_jobs": 0,
                "completed_jobs": 0,
                "failed_jobs": 0,
                "total_jobs": 0
            }
    
    async def cleanup_stale_jobs(self):
        """Clean up jobs that have been processing for too long."""
        try:
            cutoff_time = datetime.now().timestamp() - self.job_timeout
            
            # Get stale processing jobs
            stale_jobs = await self.redis_client.zrangebyscore(
                self.processing_queue, 
                min=0, 
                max=cutoff_time
            )
            
            for job_id in stale_jobs:
                job_id = job_id.decode() if isinstance(job_id, bytes) else job_id
                await self._handle_job_failure(job_id, "Job timeout - exceeded maximum processing time")
                logger.warning(f"Cleaned up stale job: {job_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup stale jobs: {e}")