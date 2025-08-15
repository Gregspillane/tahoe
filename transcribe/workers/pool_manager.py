"""
Worker pool management for the Transcription Service.
Implements proper job claiming and processing with retry logic.
"""

import asyncio
import logging
import uuid
from typing import Dict, Optional
from datetime import datetime

from transcription.assemblyai_client import AssemblyAIClient, AssemblyAIError
from transcription.openai_client import OpenAIClient, OpenAIError
from storage.s3_manager import S3Manager, S3ManagerError
from reconciliation.reconciler import TranscriptionReconciler
from formatting.transcript_formatters import create_transcript_formatter

logger = logging.getLogger(__name__)


class WorkerPoolManager:
    """Manages a pool of transcription workers with job claiming and processing."""
    
    def __init__(
        self, 
        job_manager, 
        assemblyai_api_key: str,
        openai_api_key: str,
        openai_model: str,
        google_api_key: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str,
        s3_transcript_bucket: str,
        gemini_model: str = "gemini-2.5-pro",
        gemini_max_tokens: int = 8192,
        gemini_temperature: float = 0.1,
        worker_count: int = 4
    ):
        self.job_manager = job_manager
        self.worker_count = worker_count
        self.workers = []
        self.running = False
        self.worker_stats = {}
        
        # Store S3 transcript bucket for Phase 5 storage
        self.s3_transcript_bucket = s3_transcript_bucket
        
        # Initialize transcription clients
        self.assemblyai_client = AssemblyAIClient(assemblyai_api_key)
        self.openai_client = OpenAIClient(
            api_key=openai_api_key,
            model=openai_model
        )
        
        # Initialize S3 manager
        self.s3_manager = S3Manager(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region
        )
        
        # Initialize reconciliation service
        self.reconciler = TranscriptionReconciler(
            gemini_api_key=google_api_key,  # Using same Google API key for Gemini
            gemini_model=gemini_model,
            max_tokens=gemini_max_tokens,
            temperature=gemini_temperature
        )
        
        # Initialize transcript formatter
        self.formatter = create_transcript_formatter()
        
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
            # Process with both providers in parallel (AssemblyAI + Google)
            provider_results = await self._transcribe_with_both_providers(job_id, audio_file_url)
            
            # Perform Gemini reconciliation on the provider results
            reconciled_result = await self.reconciler.reconcile_provider_results(job_id, provider_results)
            
            # Format outputs and store in S3 (Phase 5 enhancement)
            try:
                formatted_outputs = self.formatter.format_reconciliation_result(
                    job_id=job_id,
                    tenant_id="default",  # TODO: Extract from job data or context
                    reconciliation_result=reconciled_result,
                    original_filename=job_data.get("original_filename")
                )
                
                # Upload formatted transcripts to S3
                s3_urls = await self.s3_manager.upload_multiple_transcript_formats(
                    bucket=self.s3_transcript_bucket,
                    tenant_id="default",
                    job_uuid=job_id,
                    raw_transcript=formatted_outputs.raw_json,
                    agent_optimized=formatted_outputs.agent_optimized_json
                )
                
                # Create enhanced result with S3 URLs and metadata
                enhanced_result = {
                    **reconciled_result,
                    "s3_storage": s3_urls,
                    "formatted_outputs": {
                        "word_count": formatted_outputs.word_count,
                        "duration_seconds": formatted_outputs.duration_seconds,
                        "display_text": formatted_outputs.display_text,
                        "display_text_preview": formatted_outputs.display_text[:200] + "..." if len(formatted_outputs.display_text) > 200 else formatted_outputs.display_text
                    }
                }
                
                logger.info(f"Successfully stored transcripts for job {job_id}: {formatted_outputs.word_count} words, S3 URLs: {list(s3_urls.keys())}")
                
            except Exception as e:
                logger.error(f"Failed to format and store outputs for job {job_id}: {e}")
                # Fallback: store reconciled result without S3 storage
                enhanced_result = {
                    **reconciled_result,
                    "storage_error": str(e)
                }
            
            # Mark job as completed with reconciled transcription result
            await self.job_manager.complete_job(
                job_id, 
                transcript_url=reconciled_result.get("s3_url", f"s3://transcripts/{job_id}/reconciled.json"),
                result_data=enhanced_result
            )
            
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
    
    async def _transcribe_with_both_providers(self, job_id: str, audio_file_url: str) -> Dict:
        """Transcribe audio using both AssemblyAI and OpenAI in parallel."""
        logger.info(f"Starting parallel transcription for job {job_id}: {audio_file_url}")
        
        # Run both transcriptions in parallel
        try:
            assemblyai_task = asyncio.create_task(
                self._transcribe_with_assemblyai(job_id, audio_file_url)
            )
            openai_task = asyncio.create_task(
                self._transcribe_with_openai(job_id, audio_file_url)
            )
            
            # Wait for both to complete
            assemblyai_result, openai_result = await asyncio.gather(
                assemblyai_task, openai_task, return_exceptions=True
            )
            
            # Handle partial failures
            results = {
                "job_id": job_id,
                "audio_file_url": audio_file_url,
                "processing_status": "completed",
                "providers": {}
            }
            
            # Process AssemblyAI result
            if isinstance(assemblyai_result, Exception):
                logger.error(f"AssemblyAI failed for job {job_id}: {assemblyai_result}")
                results["providers"]["assemblyai"] = {
                    "status": "failed",
                    "error": str(assemblyai_result)
                }
            else:
                results["providers"]["assemblyai"] = {
                    "status": "completed",
                    "result": assemblyai_result
                }
            
            # Process OpenAI result
            if isinstance(openai_result, Exception):
                logger.error(f"OpenAI failed for job {job_id}: {openai_result}")
                results["providers"]["openai"] = {
                    "status": "failed",
                    "error": str(openai_result)
                }
            else:
                results["providers"]["openai"] = {
                    "status": "completed",
                    "result": openai_result
                }
            
            # Check if at least one provider succeeded
            successful_providers = [
                provider for provider, data in results["providers"].items() 
                if data["status"] == "completed"
            ]
            
            if not successful_providers:
                # Both providers failed
                raise Exception("Both AssemblyAI and Google Speech transcription failed")
            
            # Generate S3 URL for combined results
            results["s3_url"] = f"s3://transcripts/{job_id}/combined.json"
            
            logger.info(f"Parallel transcription completed for job {job_id}. Successful providers: {successful_providers}")
            return results
            
        except Exception as e:
            logger.error(f"Parallel transcription failed for job {job_id}: {e}")
            raise Exception(f"Parallel transcription failed: {str(e)}")
    
    async def _transcribe_with_assemblyai(self, job_id: str, audio_file_url: str) -> Dict:
        """Transcribe audio using AssemblyAI service with presigned URL."""
        logger.debug(f"Starting AssemblyAI transcription for job {job_id}")
        
        try:
            # Generate presigned URL for AssemblyAI access
            presigned_url = self.s3_manager.generate_presigned_url(audio_file_url, expiration_hours=2)
            
            # Call AssemblyAI transcription with presigned URL
            transcript_result = await self.assemblyai_client.transcribe_audio(presigned_url, job_id)
            logger.debug(f"AssemblyAI transcription completed for job {job_id}")
            return transcript_result
            
        except (AssemblyAIError, S3ManagerError) as e:
            logger.error(f"AssemblyAI transcription failed for job {job_id}: {e}")
            raise Exception(f"AssemblyAI transcription failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in AssemblyAI transcription for job {job_id}: {e}")
            raise Exception(f"AssemblyAI transcription failed: {str(e)}")
    
    async def _transcribe_with_openai(self, job_id: str, audio_file_url: str) -> Dict:
        """Transcribe audio using OpenAI gpt-4o-transcribe service."""
        logger.debug(f"Starting OpenAI transcription for job {job_id}")
        
        try:
            # Call OpenAI transcription (downloads from S3 internally)
            transcript_result = await self.openai_client.transcribe_audio(audio_file_url, job_id, self.s3_manager)
            logger.debug(f"OpenAI transcription completed for job {job_id}")
            return transcript_result
            
        except (OpenAIError, S3ManagerError) as e:
            logger.error(f"OpenAI transcription failed for job {job_id}: {e}")
            raise Exception(f"OpenAI transcription failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI transcription for job {job_id}: {e}")
            raise Exception(f"OpenAI transcription failed: {str(e)}")
    
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