"""
Worker pool management for the Transcription Service.
Implements proper job claiming and processing with retry logic.
"""

import asyncio
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkerPoolManager:
    """Manages a pool of transcription workers with job claiming and processing."""
    
    def __init__(self, job_manager, worker_count: int = 4):
        self.job_manager = job_manager
        self.worker_count = worker_count
        self.workers = []
        self.running = False
        self.worker_stats = {}
        
        # Worker settings
        self.poll_interval = 5  # seconds between job polling
        self.stale_job_check_interval = 300  # 5 minutes between stale job cleanup
        
    async def start(self):
        """Start the worker pool."""
        self.running = True
        logger.info(f"Starting {self.worker_count} workers")
        
        # Start worker tasks
        for i in range(self.worker_count):
            worker_id = f"worker-{i}-{uuid.uuid4().hex[:8]}"
            worker_task = asyncio.create_task(self._worker_loop(worker_id))
            self.workers.append((worker_id, worker_task))
            
            # Initialize worker stats
            self.worker_stats[worker_id] = {
                "jobs_processed": 0,
                "jobs_failed": 0,
                "last_job_at": None,
                "status": "idle"
            }
        
        # Start stale job cleanup task
        cleanup_task = asyncio.create_task(self._stale_job_cleanup_loop())
        self.workers.append(("cleanup", cleanup_task))
        
        logger.info(f"Started {len(self.workers)} workers")
    
    async def stop(self):
        """Stop the worker pool."""
        self.running = False
        logger.info("Stopping worker pool")
        
        # Cancel all workers
        for worker_id, worker_task in self.workers:
            worker_task.cancel()
        
        # Wait for workers to finish
        tasks = [worker_task for _, worker_task in self.workers]
        await asyncio.gather(*tasks, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Worker pool stopped")
    
    def get_status(self) -> Dict:
        """Get worker pool status."""
        active_workers = sum(1 for _, w in self.workers if not w.done())
        
        return {
            "worker_count": len([w for w in self.workers if w[0] != "cleanup"]),
            "running": self.running,
            "active_workers": active_workers,
            "worker_stats": self.worker_stats.copy()
        }
    
    async def _worker_loop(self, worker_id: str):
        """Main worker loop - claims and processes jobs."""
        logger.info(f"Worker {worker_id} started")
        
        try:
            while self.running:
                try:
                    # Try to claim a job
                    job_data = await self.job_manager.claim_job(worker_id)
                    
                    if job_data:
                        # Process the job
                        await self._process_job(worker_id, job_data)
                    else:
                        # No jobs available, wait before polling again
                        await asyncio.sleep(self.poll_interval)
                        
                except Exception as e:
                    logger.error(f"Worker {worker_id} error in main loop: {e}")
                    await asyncio.sleep(self.poll_interval)
                    
        except asyncio.CancelledError:
            logger.info(f"Worker {worker_id} cancelled")
        except Exception as e:
            logger.error(f"Worker {worker_id} fatal error: {e}")
        finally:
            logger.info(f"Worker {worker_id} stopped")
    
    async def _process_job(self, worker_id: str, job_data: Dict):
        """Process a single transcription job."""
        job_id = job_data.get("job_id")
        audio_file_url = job_data.get("audio_file_url")
        
        logger.info(f"Worker {worker_id} processing job {job_id}: {audio_file_url}")
        
        # Update worker stats
        self.worker_stats[worker_id]["status"] = "processing"
        self.worker_stats[worker_id]["last_job_at"] = datetime.now().isoformat()
        
        try:
            # Simulate transcription processing for now
            # In Phase 3, this will call the actual transcription services
            await self._simulate_transcription_work(job_id, audio_file_url)
            
            # Mark job as completed
            transcript_url = f"s3://transcripts/{job_id}/final.md"
            await self.job_manager.complete_job(job_id, transcript_url=transcript_url)
            
            # Update stats
            self.worker_stats[worker_id]["jobs_processed"] += 1
            logger.info(f"Worker {worker_id} completed job {job_id}")
            
        except Exception as e:
            # Mark job as failed
            error_message = f"Worker {worker_id} failed to process job: {str(e)}"
            await self.job_manager.complete_job(job_id, error_message=error_message)
            
            # Update stats
            self.worker_stats[worker_id]["jobs_failed"] += 1
            logger.error(f"Worker {worker_id} failed job {job_id}: {e}")
            
        finally:
            # Reset worker status
            self.worker_stats[worker_id]["status"] = "idle"
    
    async def _simulate_transcription_work(self, job_id: str, audio_file_url: str):
        """Simulate transcription work for MVP testing."""
        # Simulate variable processing time (2-10 seconds)
        import random
        processing_time = random.uniform(2, 10)
        
        logger.info(f"Simulating transcription for job {job_id} (taking {processing_time:.1f}s)")
        await asyncio.sleep(processing_time)
        
        # Simulate occasional failures for testing retry logic
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Simulated transcription failure")
        
        logger.info(f"Simulated transcription completed for job {job_id}")
    
    async def _stale_job_cleanup_loop(self):
        """Periodic cleanup of stale jobs."""
        logger.info("Stale job cleanup task started")
        
        try:
            while self.running:
                try:
                    await self.job_manager.cleanup_stale_jobs()
                    await asyncio.sleep(self.stale_job_check_interval)
                except Exception as e:
                    logger.error(f"Error in stale job cleanup: {e}")
                    await asyncio.sleep(self.stale_job_check_interval)
                    
        except asyncio.CancelledError:
            logger.info("Stale job cleanup task cancelled")
        except Exception as e:
            logger.error(f"Stale job cleanup fatal error: {e}")
        finally:
            logger.info("Stale job cleanup task stopped")