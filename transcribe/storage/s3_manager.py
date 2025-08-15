"""
Unified S3 manager for secure file handling in the Transcription Service.
Provides both download-to-temp and presigned URL patterns for different providers.
"""

import os
import boto3
import asyncio
import tempfile
import logging
import json
from pathlib import Path
from typing import Optional, Tuple, Dict
from botocore.exceptions import ClientError, NoCredentialsError
from urllib.parse import urlparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class S3ManagerError(Exception):
    """Custom exception for S3Manager operations."""
    pass


class S3Manager:
    """Unified S3 manager for transcription service file operations."""
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str):
        """Initialize S3 manager with AWS credentials."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
            )
            
            # Test credentials on initialization
            self.s3_client.list_buckets()
            logger.info("S3Manager initialized successfully")
            
        except NoCredentialsError as e:
            logger.error("AWS credentials not found or invalid")
            raise S3ManagerError("Invalid AWS credentials") from e
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise S3ManagerError(f"S3 client initialization failed: {str(e)}") from e
    
    def parse_s3_url(self, s3_url: str) -> Tuple[str, str]:
        """Parse S3 URL into bucket and key components.
        
        Args:
            s3_url: S3 URL in format s3://bucket/key/path
            
        Returns:
            Tuple of (bucket_name, object_key)
        """
        if not s3_url.startswith('s3://'):
            raise S3ManagerError(f"Invalid S3 URL format: {s3_url}")
        
        parsed = urlparse(s3_url)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        
        if not bucket or not key:
            raise S3ManagerError(f"Invalid S3 URL components: {s3_url}")
        
        return bucket, key
    
    async def download_to_temp(self, s3_url: str, job_id: str) -> str:
        """Download S3 file to temporary storage for processing.
        
        Args:
            s3_url: S3 URL to download
            job_id: Job ID for file naming
            
        Returns:
            Path to downloaded temporary file
        """
        logger.info(f"Downloading {s3_url} for job {job_id}")
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            # Create temp directory
            temp_dir = Path("/tmp/transcription")
            temp_dir.mkdir(exist_ok=True)
            
            # Generate temp file path with job ID and original extension
            file_extension = self._get_file_extension(key)
            temp_file_path = temp_dir / f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
            
            # Download file
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.s3_client.download_file(bucket, key, str(temp_file_path))
            )
            
            # Verify file was downloaded
            if not temp_file_path.exists():
                raise S3ManagerError(f"File download failed: {temp_file_path}")
            
            file_size = temp_file_path.stat().st_size
            logger.info(f"Downloaded {s3_url} to {temp_file_path} ({file_size} bytes)")
            
            return str(temp_file_path)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                raise S3ManagerError(f"S3 bucket not found: {bucket}")
            elif error_code == 'NoSuchKey':
                raise S3ManagerError(f"S3 object not found: {s3_url}")
            elif error_code == 'AccessDenied':
                raise S3ManagerError(f"Access denied to S3 object: {s3_url}")
            else:
                raise S3ManagerError(f"S3 download error: {e}")
        except Exception as e:
            logger.error(f"Failed to download {s3_url}: {e}")
            raise S3ManagerError(f"Download failed: {str(e)}") from e
    
    def generate_presigned_url(self, s3_url: str, expiration_hours: int = 1) -> str:
        """Generate presigned URL for S3 object access.
        
        Args:
            s3_url: S3 URL to create presigned URL for
            expiration_hours: URL expiration time in hours
            
        Returns:
            Presigned URL string
        """
        logger.info(f"Generating presigned URL for {s3_url}")
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration_hours * 3600  # Convert hours to seconds
            )
            
            logger.info(f"Generated presigned URL for {s3_url} (expires in {expiration_hours}h)")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {s3_url}: {e}")
            raise S3ManagerError(f"Presigned URL generation failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            raise S3ManagerError(f"Presigned URL failed: {str(e)}") from e
    
    async def cleanup_temp_file(self, file_path: str) -> bool:
        """Clean up temporary file after processing.
        
        Args:
            file_path: Path to temporary file to delete
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                await asyncio.get_event_loop().run_in_executor(
                    None, os.remove, file_path
                )
                logger.info(f"Cleaned up temporary file: {file_path}")
                return True
            else:
                logger.warning(f"Temporary file not found for cleanup: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to cleanup temporary file {file_path}: {e}")
            return False
    
    def _get_file_extension(self, file_path: str) -> str:
        """Extract file extension from path."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Supported audio formats
        supported_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma']
        
        if extension in supported_extensions:
            return extension
        else:
            # Default to .mp3 if unknown extension
            logger.warning(f"Unknown audio extension {extension}, defaulting to .mp3")
            return '.mp3'
    
    async def validate_s3_access(self, s3_url: str) -> bool:
        """Validate that S3 object exists and is accessible.
        
        Args:
            s3_url: S3 URL to validate
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            # Check if object exists and get metadata
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.head_object(Bucket=bucket, Key=key)
            )
            
            logger.info(f"S3 object validated: {s3_url}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"S3 validation failed for {s3_url}: {error_code}")
            return False
        except Exception as e:
            logger.error(f"S3 validation error for {s3_url}: {e}")
            return False
    
    def get_file_info(self, s3_url: str) -> Optional[dict]:
        """Get file metadata from S3.
        
        Args:
            s3_url: S3 URL to get info for
            
        Returns:
            Dict with file metadata or None if not accessible
        """
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            response = self.s3_client.head_object(Bucket=bucket, Key=key)
            
            return {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag', '').strip('"'),
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {s3_url}: {e}")
            return None
    
    # Phase 5: Multi-tenant UUID-based storage methods
    
    def generate_tenant_uuid_path(self, tenant_id: str, job_uuid: str, filename: str, bucket: str = None) -> str:
        """
        Generate S3 path using tenant/UUID structure for Phase 5.
        
        Args:
            tenant_id: Tenant identifier
            job_uuid: Job UUID identifier
            filename: Name of the file (e.g., 'raw_transcript.json', 'agent_optimized.json')
            bucket: S3 bucket name (optional, for full S3 URL)
            
        Returns:
            S3 path or full S3 URL if bucket provided
        """
        path = f"{tenant_id}/{job_uuid}/{filename}"
        
        if bucket:
            return f"s3://{bucket}/{path}"
        
        return path
    
    async def upload_transcript_data(
        self,
        bucket: str,
        tenant_id: str,
        job_uuid: str,
        transcript_data: Dict,
        format_type: str = "raw"
    ) -> str:
        """
        Upload transcript data to S3 with tenant/UUID structure.
        
        Args:
            bucket: S3 bucket name
            tenant_id: Tenant identifier
            job_uuid: Job UUID identifier
            transcript_data: Dictionary data to upload as JSON
            format_type: Type of format ('raw', 'agent_optimized')
            
        Returns:
            S3 URL of uploaded file
        """
        filename = f"{format_type}_transcript.json"
        s3_path = self.generate_tenant_uuid_path(tenant_id, job_uuid, filename)
        s3_url = f"s3://{bucket}/{s3_path}"
        
        logger.info(f"Uploading {format_type} transcript for job {job_uuid} to {s3_url}")
        
        try:
            # Convert data to JSON
            json_data = json.dumps(transcript_data, indent=2, default=str)
            
            # Upload to S3
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.put_object(
                    Bucket=bucket,
                    Key=s3_path,
                    Body=json_data,
                    ContentType='application/json',
                    Metadata={
                        'tenant_id': tenant_id,
                        'job_uuid': job_uuid,
                        'format_type': format_type,
                        'upload_timestamp': datetime.now().isoformat()
                    }
                )
            )
            
            logger.info(f"Successfully uploaded {format_type} transcript: {s3_url}")
            return s3_url
            
        except Exception as e:
            logger.error(f"Failed to upload {format_type} transcript to {s3_url}: {e}")
            raise S3ManagerError(f"Upload failed: {str(e)}") from e
    
    async def upload_multiple_transcript_formats(
        self,
        bucket: str,
        tenant_id: str,
        job_uuid: str,
        raw_transcript: Dict,
        agent_optimized: Dict
    ) -> Dict[str, str]:
        """
        Upload multiple transcript formats for a single job.
        
        Args:
            bucket: S3 bucket name
            tenant_id: Tenant identifier
            job_uuid: Job UUID identifier
            raw_transcript: Raw transcript data
            agent_optimized: Agent-optimized transcript data
            
        Returns:
            Dictionary mapping format types to S3 URLs
        """
        logger.info(f"Uploading multiple transcript formats for job {job_uuid}")
        
        try:
            # Upload both formats in parallel
            raw_task = asyncio.create_task(
                self.upload_transcript_data(bucket, tenant_id, job_uuid, raw_transcript, "raw")
            )
            agent_task = asyncio.create_task(
                self.upload_transcript_data(bucket, tenant_id, job_uuid, agent_optimized, "agent_optimized")
            )
            
            raw_url, agent_url = await asyncio.gather(raw_task, agent_task)
            
            result = {
                "raw_transcript_url": raw_url,
                "agent_optimized_url": agent_url
            }
            
            logger.info(f"Successfully uploaded all formats for job {job_uuid}: {list(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload multiple formats for job {job_uuid}: {e}")
            raise S3ManagerError(f"Multi-format upload failed: {str(e)}") from e
    
    async def retrieve_transcript_data(self, s3_url: str) -> Dict:
        """
        Retrieve and parse transcript data from S3.
        
        Args:
            s3_url: S3 URL to retrieve
            
        Returns:
            Parsed JSON data
        """
        logger.info(f"Retrieving transcript data from {s3_url}")
        
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            # Download object
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=bucket, Key=key)
            )
            
            # Parse JSON data
            json_data = response['Body'].read().decode('utf-8')
            transcript_data = json.loads(json_data)
            
            logger.info(f"Successfully retrieved transcript data from {s3_url}")
            return transcript_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in transcript file {s3_url}: {e}")
            raise S3ManagerError(f"JSON parsing failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Failed to retrieve transcript data from {s3_url}: {e}")
            raise S3ManagerError(f"Retrieval failed: {str(e)}") from e
    
    def generate_presigned_download_url(self, s3_url: str, expiration_hours: int = 24) -> str:
        """
        Generate presigned URL for transcript download with longer expiration.
        
        Args:
            s3_url: S3 URL to create presigned URL for
            expiration_hours: URL expiration time in hours (default 24h for transcript access)
            
        Returns:
            Presigned URL string
        """
        return self.generate_presigned_url(s3_url, expiration_hours)
    
    async def list_tenant_jobs(self, bucket: str, tenant_id: str, limit: int = 100) -> list:
        """
        List jobs for a specific tenant from S3.
        
        Args:
            bucket: S3 bucket name
            tenant_id: Tenant identifier
            limit: Maximum number of jobs to return
            
        Returns:
            List of job UUIDs for the tenant
        """
        logger.info(f"Listing jobs for tenant {tenant_id}")
        
        try:
            # List objects with tenant prefix
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=f"{tenant_id}/",
                    Delimiter="/",
                    MaxKeys=limit
                )
            )
            
            # Extract job UUIDs from prefixes
            job_uuids = []
            for prefix in response.get('CommonPrefixes', []):
                # Extract UUID from prefix like "tenant_id/uuid/"
                parts = prefix['Prefix'].rstrip('/').split('/')
                if len(parts) >= 2:
                    job_uuids.append(parts[1])
            
            logger.info(f"Found {len(job_uuids)} jobs for tenant {tenant_id}")
            return job_uuids
            
        except Exception as e:
            logger.error(f"Failed to list jobs for tenant {tenant_id}: {e}")
            raise S3ManagerError(f"Job listing failed: {str(e)}") from e
    
    async def delete_job_data(self, bucket: str, tenant_id: str, job_uuid: str) -> bool:
        """
        Delete all data for a specific job.
        
        Args:
            bucket: S3 bucket name
            tenant_id: Tenant identifier
            job_uuid: Job UUID identifier
            
        Returns:
            True if deletion successful
        """
        logger.info(f"Deleting job data for {tenant_id}/{job_uuid}")
        
        try:
            # List all objects for this job
            prefix = f"{tenant_id}/{job_uuid}/"
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            )
            
            # Delete all objects
            objects_to_delete = []
            for obj in response.get('Contents', []):
                objects_to_delete.append({'Key': obj['Key']})
            
            if objects_to_delete:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.s3_client.delete_objects(
                        Bucket=bucket,
                        Delete={'Objects': objects_to_delete}
                    )
                )
                
                logger.info(f"Deleted {len(objects_to_delete)} objects for job {job_uuid}")
            else:
                logger.info(f"No objects found for job {job_uuid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job data for {job_uuid}: {e}")
            return False