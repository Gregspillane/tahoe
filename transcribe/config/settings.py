"""
Pydantic settings configuration for the Transcription Service.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings."""
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(..., env="REDIS_URL")
    
    # AWS S3 Configuration
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_audio_bucket: str = Field(..., env="S3_AUDIO_BUCKET")
    s3_transcript_bucket: str = Field(..., env="S3_TRANSCRIPT_BUCKET")
    
    # Transcription Service API Keys
    assemblyai_api_key: str = Field(..., env="ASSEMBLYAI_API_KEY")
    
    # Google Cloud Configuration
    google_project_id: str = Field(..., env="GOOGLE_PROJECT_ID")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    google_application_credentials: Optional[str] = Field(None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Service Authentication
    service_auth_token: str = Field(..., env="SERVICE_AUTH_TOKEN")
    
    # Processing Configuration
    poll_interval: int = Field(default=60, env="POLL_INTERVAL")
    worker_count: int = Field(default=4, env="WORKER_COUNT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    job_timeout: int = Field(default=1800, env="JOB_TIMEOUT")  # 30 minutes
    
    # Google Cloud Speech Configuration
    google_speech_model: str = Field(default="chirp_2", env="GOOGLE_SPEECH_MODEL")
    google_language_code: str = Field(default="en-US", env="GOOGLE_LANGUAGE_CODE")
    
    # Google Gemini API Configuration for Reconciliation
    gemini_model: str = Field(default="gemini-2.5-pro", env="GEMINI_MODEL")
    gemini_max_tokens: int = Field(default=8192, env="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(default=0.1, env="GEMINI_TEMPERATURE")  # Low for consistent reconciliation
    
    # Service Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")
    port: int = Field(default=9100, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Allow extra fields in .env without error
    }