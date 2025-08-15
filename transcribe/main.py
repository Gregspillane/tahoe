"""
Transcription Service - Main Application Entry Point

Multi-provider transcription service with intelligent reconciliation
using AssemblyAI and Google Cloud Speech Chirp 2.
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import Settings
from middleware.authentication import get_current_user
from storage.file_discovery import FileDiscoveryService
from jobs.job_manager import JobManager
from workers.pool_manager import WorkerPoolManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global settings
settings = Settings()

# Global services (will be initialized in lifespan)
file_discovery_service = None
job_manager = None
worker_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global file_discovery_service, job_manager, worker_pool
    
    logger.info("Starting Transcription Service...")
    
    try:
        # Initialize core services
        logger.info("Initializing services...")
        
        # Initialize job manager (Redis connection)
        job_manager = JobManager(settings.redis_url)
        await job_manager.initialize()
        
        # Initialize worker pool
        worker_pool = WorkerPoolManager(
            job_manager=job_manager,
            assemblyai_api_key=settings.assemblyai_api_key,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            google_api_key=settings.google_api_key,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            aws_region=settings.aws_region,
            s3_transcript_bucket=settings.s3_transcript_bucket,
            gemini_model=settings.gemini_model,
            gemini_max_tokens=settings.gemini_max_tokens,
            gemini_temperature=settings.gemini_temperature,
            worker_count=settings.worker_count
        )
        await worker_pool.start()
        
        # Initialize file discovery service
        file_discovery_service = FileDiscoveryService(
            job_manager=job_manager,
            poll_interval=settings.poll_interval
        )
        await file_discovery_service.start()
        
        logger.info("All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down services...")
        
        if file_discovery_service:
            await file_discovery_service.stop()
        
        if worker_pool:
            await worker_pool.stop()
        
        if job_manager:
            await job_manager.close()
        
        logger.info("Services shut down complete")


# Create FastAPI application
app = FastAPI(
    title="Transcription Service",
    description="Multi-provider transcription service with intelligent reconciliation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health and Status Endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "transcription"}


@app.get("/status")
async def service_status():
    """Detailed service status and metrics."""
    try:
        # Check Redis connection
        redis_status = "healthy" if job_manager and await job_manager.health_check() else "unhealthy"
        
        # Get queue statistics
        queue_stats = await job_manager.get_queue_stats() if job_manager else {}
        
        # Get worker status
        worker_status = worker_pool.get_status() if worker_pool else {}
        
        return {
            "status": "operational",
            "services": {
                "redis": redis_status,
                "workers": worker_status,
                "file_discovery": "running" if file_discovery_service else "stopped"
            },
            "queue": queue_stats,
            "settings": {
                "worker_count": settings.worker_count,
                "poll_interval": settings.poll_interval,
                "max_retries": settings.max_retries
            }
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Service status check failed")


# Transcription Management Endpoints
@app.post("/transcribe/submit")
async def submit_transcription(
    audio_file_url: str,
    client_id: str = None,
    priority: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Submit audio file for transcription."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Create transcription job
        job_id = await job_manager.create_job(
            audio_file_url=audio_file_url,
            client_id=client_id,
            priority=priority
        )
        
        logger.info(f"Created transcription job {job_id} for {audio_file_url}")
        
        return {
            "job_id": job_id,
            "status": "submitted",
            "message": "Transcription job submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit transcription job: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit transcription job")


# Test endpoint without authentication for MVP testing
@app.post("/test/submit-job")
async def test_submit_job(audio_file_url: str, client_id: str = "test", priority: int = 0):
    """Test endpoint to submit jobs without authentication."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        job_id = await job_manager.create_job(
            audio_file_url=audio_file_url,
            client_id=client_id,
            priority=priority
        )
        
        logger.info(f"TEST: Created job {job_id} for {audio_file_url}")
        
        return {
            "job_id": job_id,
            "status": "submitted",
            "audio_file_url": audio_file_url,
            "client_id": client_id,
            "priority": priority
        }
        
    except Exception as e:
        logger.error(f"Test job submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test/job-status/{job_id}")
async def test_get_job_status(job_id: str):
    """Test endpoint to get job status without authentication."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        status = await job_manager.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transcribe/status/{job_id}")
async def get_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get transcription job status."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        status = await job_manager.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/transcribe/result/{job_id}")
async def get_transcript(job_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieve completed transcript."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        result = await job_manager.get_job_result(job_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job or result not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transcript")


@app.post("/transcribe/bulk-status")
async def get_bulk_status(
    job_ids: list[str],
    current_user: dict = Depends(get_current_user)
):
    """Check multiple job statuses."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        statuses = await job_manager.get_bulk_status(job_ids)
        
        return {"statuses": statuses}
        
    except Exception as e:
        logger.error(f"Failed to get bulk status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bulk status")


# Phase 5: Enhanced API Endpoints for Production Use

@app.get("/jobs/{job_uuid}/status")
async def get_job_status_by_uuid(job_uuid: str, current_user: dict = Depends(get_current_user)):
    """Get job processing status by UUID (Phase 5 enhancement)."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # For now, use existing job manager (will be enhanced with new database tables)
        status = await job_manager.get_job_status(job_uuid)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job_uuid,
            "status": status.get("status"),
            "processing_metadata": {
                "created_at": status.get("created_at"),
                "started_at": status.get("started_at"),
                "completed_at": status.get("completed_at"),
                "retry_count": status.get("retry_count"),
                "worker_id": status.get("worker_id")
            },
            "error_message": status.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status by UUID: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")


@app.get("/jobs/{job_uuid}/transcript")
async def get_job_transcript(job_uuid: str, format_type: str = "display", current_user: dict = Depends(get_current_user)):
    """Get transcript for a job in specified format (Phase 5 enhancement)."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get job result
        result = await job_manager.get_job_result(job_uuid)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job or transcript not found")
        
        # Extract formatted outputs from Phase 5 enhancement
        formatted_outputs = result.get("formatted_outputs", {})
        s3_storage = result.get("s3_storage", {})
        
        if format_type == "display":
            # Return display text for web UI
            display_text = formatted_outputs.get("display_text", "")
            if not display_text:
                # Fallback to final transcript
                display_text = result.get("final_transcript", "")
            
            return {
                "job_id": job_uuid,
                "format": "display",
                "transcript": display_text,
                "metadata": {
                    "word_count": formatted_outputs.get("word_count", 0),
                    "duration_seconds": formatted_outputs.get("duration_seconds"),
                    "confidence_score": result.get("confidence_score", 0.0)
                }
            }
        
        elif format_type == "raw":
            # Return reference to raw transcript S3 URL
            raw_url = s3_storage.get("raw_transcript_url")
            if not raw_url:
                raise HTTPException(status_code=404, detail="Raw transcript not available")
            
            # Generate presigned URL for download
            if worker_pool and worker_pool.s3_manager:
                presigned_url = worker_pool.s3_manager.generate_presigned_download_url(raw_url, 24)
                
                return {
                    "job_id": job_uuid,
                    "format": "raw",
                    "download_url": presigned_url,
                    "s3_url": raw_url,
                    "expires_in_hours": 24
                }
            else:
                return {
                    "job_id": job_uuid,
                    "format": "raw",
                    "s3_url": raw_url,
                    "note": "Direct S3 access required"
                }
        
        elif format_type == "agent_optimized":
            # Return reference to agent-optimized transcript S3 URL
            agent_url = s3_storage.get("agent_optimized_url")
            if not agent_url:
                raise HTTPException(status_code=404, detail="Agent-optimized transcript not available")
            
            # Generate presigned URL for download
            if worker_pool and worker_pool.s3_manager:
                presigned_url = worker_pool.s3_manager.generate_presigned_download_url(agent_url, 24)
                
                return {
                    "job_id": job_uuid,
                    "format": "agent_optimized",
                    "download_url": presigned_url,
                    "s3_url": agent_url,
                    "expires_in_hours": 24
                }
            else:
                return {
                    "job_id": job_uuid,
                    "format": "agent_optimized",
                    "s3_url": agent_url,
                    "note": "Direct S3 access required"
                }
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format type. Use 'display', 'raw', or 'agent_optimized'")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transcript")


@app.get("/jobs/{job_uuid}/metrics")
async def get_job_metrics(job_uuid: str, current_user: dict = Depends(get_current_user)):
    """Get quality metrics and reconciliation summary for a job (Phase 5 enhancement)."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get job result
        result = await job_manager.get_job_result(job_uuid)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Extract reconciliation metadata
        reconciliation_metadata = result.get("reconciliation_metadata", {})
        formatted_outputs = result.get("formatted_outputs", {})
        
        return {
            "job_id": job_uuid,
            "quality_metrics": {
                "overall_confidence": result.get("confidence_score", 0.0),
                "word_count": formatted_outputs.get("word_count", 0),
                "duration_seconds": formatted_outputs.get("duration_seconds"),
                "processing_time": result.get("processing_time_seconds", 0.0)
            },
            "reconciliation_summary": {
                "method": reconciliation_metadata.get("method", "unknown"),
                "segments_processed": reconciliation_metadata.get("segments_processed", 0),
                "discrepancies_found": reconciliation_metadata.get("discrepancies_found", 0),
                "provider_performance": {
                    "assemblyai_segments": reconciliation_metadata.get("segments_from_assemblyai", 0),
                    "google_segments": reconciliation_metadata.get("segments_from_google", 0),
                    "reconciled_segments": reconciliation_metadata.get("segments_reconciled", 0),
                    "agreed_segments": reconciliation_metadata.get("segments_agreed", 0)
                }
            },
            "audit_trail": {
                "total_decisions": len(result.get("audit_trail", {}).get("decisions", [])),
                "reconciliation_status": result.get("reconciliation_status", "unknown"),
                "timestamp": reconciliation_metadata.get("timestamp")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job metrics")


@app.get("/tenants/{tenant_id}/jobs")
async def list_tenant_jobs(
    tenant_id: str, 
    limit: int = 50, 
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """List jobs for a specific tenant (Phase 5 enhancement)."""
    try:
        # For MVP, return placeholder response
        # This would be implemented with the new JobRecord table in full Phase 5
        
        return {
            "tenant_id": tenant_id,
            "jobs": [],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": 0
            },
            "note": "Full tenant job listing will be implemented with JobRecord table integration"
        }
        
    except Exception as e:
        logger.error(f"Failed to list tenant jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list tenant jobs")


@app.post("/jobs/{job_uuid}/reprocess")
async def reprocess_job(job_uuid: str, current_user: dict = Depends(get_current_user)):
    """Trigger reprocessing of a job (Phase 5 enhancement)."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Check if job exists
        status = await job_manager.get_job_status(job_uuid)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # For MVP, create a new job with same audio file URL
        audio_file_url = status.get("audio_file_url")
        if not audio_file_url:
            raise HTTPException(status_code=400, detail="Cannot reprocess job without audio file URL")
        
        # Create new job for reprocessing
        new_job_id = await job_manager.create_job(
            audio_file_url=audio_file_url,
            client_id=status.get("client_id", "reprocess"),
            priority=1  # Higher priority for reprocessing
        )
        
        logger.info(f"Created reprocessing job {new_job_id} for original job {job_uuid}")
        
        return {
            "original_job_id": job_uuid,
            "new_job_id": new_job_id,
            "status": "reprocessing_started",
            "message": "New job created for reprocessing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reprocess job: {e}")
        raise HTTPException(status_code=500, detail="Failed to reprocess job")


# Test endpoints for Phase 5 functionality
@app.get("/test/jobs/{job_uuid}/transcript")
async def test_get_job_transcript(job_uuid: str, format_type: str = "display"):
    """Test endpoint to get transcript without authentication."""
    try:
        if not job_manager:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Get job result
        result = await job_manager.get_job_result(job_uuid)
        
        if not result:
            raise HTTPException(status_code=404, detail="Job or transcript not found")
        
        # Extract formatted outputs from Phase 5 enhancement
        formatted_outputs = result.get("formatted_outputs", {})
        s3_storage = result.get("s3_storage", {})
        
        return {
            "job_id": job_uuid,
            "format": format_type,
            "phase_5_enhancements": {
                "formatted_outputs_available": bool(formatted_outputs),
                "s3_storage_available": bool(s3_storage),
                "word_count": formatted_outputs.get("word_count", 0),
                "duration_seconds": formatted_outputs.get("duration_seconds"),
                "s3_urls": list(s3_storage.keys()) if s3_storage else []
            },
            "display_text_preview": formatted_outputs.get("display_text_preview", ""),
            "reconciliation_status": result.get("reconciliation_status", "unknown"),
            "confidence_score": result.get("confidence_score", 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test transcript retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    """Run the application directly for development."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )