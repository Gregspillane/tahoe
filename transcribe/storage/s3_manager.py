"""
Unified S3 manager for secure file handling in the Transcription Service.
Provides both download-to-temp and presigned URL patterns for different providers.
"""

import os
import boto3
import asyncio
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
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