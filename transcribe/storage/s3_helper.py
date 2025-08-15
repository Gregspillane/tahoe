"""S3 helper utilities for downloading files."""

import os
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class S3Helper:
    """Helper class for S3 operations."""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    def parse_s3_url(self, s3_url: str) -> tuple:
        """Parse S3 URL into bucket and key.
        
        Args:
            s3_url: S3 URL in format s3://bucket/key
            
        Returns:
            Tuple of (bucket, key)
        """
        parsed = urlparse(s3_url)
        if parsed.scheme != 's3':
            raise ValueError(f"Not an S3 URL: {s3_url}")
        
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        
        return bucket, key
    
    def download_file(self, s3_url: str, local_path: str) -> bool:
        """Download file from S3 to local path.
        
        Args:
            s3_url: S3 URL to download
            local_path: Local path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            logger.info(f"Downloading {s3_url} to {local_path}")
            self.s3_client.download_file(bucket, key, local_path)
            
            logger.info(f"Successfully downloaded {s3_url}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS S3 error downloading {s3_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error downloading {s3_url}: {e}")
            return False
    
    def generate_presigned_url(self, s3_url: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for S3 object.
        
        Args:
            s3_url: S3 URL to create presigned URL for
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL string
        """
        try:
            bucket, key = self.parse_s3_url(s3_url)
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {s3_url}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Error generating presigned URL for {s3_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating presigned URL for {s3_url}: {e}")
            raise