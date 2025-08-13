"""
Centralized Configuration System for Tahoe Agent Engine

This module provides environment-aware configuration management:
- Development: Loads from root .env file
- Staging/Production: Uses environment variables (from Helm/Vault)
- Supports service-specific overrides
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_DEVELOPMENT = ENVIRONMENT == "development"
IS_STAGING = ENVIRONMENT == "staging"
IS_PRODUCTION = ENVIRONMENT == "production"


def load_environment_config():
    """Load environment configuration based on deployment context."""
    if IS_DEVELOPMENT:
        # In development, load from root .env file
        root_env_path = Path(__file__).parent.parent.parent.parent / ".env"
        if root_env_path.exists():
            load_dotenv(root_env_path)
            print(f"✓ Loaded development config from {root_env_path}")
        else:
            print(f"⚠ Root .env file not found at {root_env_path}")
    else:
        # In staging/production, rely on environment variables from Helm/Vault
        print(f"✓ Using environment variables for {ENVIRONMENT} deployment")


# Load configuration on import
load_environment_config()


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    host: str = Field(default="localhost", env="DATABASE_HOST")
    port: int = Field(default=5432, env="DATABASE_PORT")
    name: str = Field(default="tahoe", env="DATABASE_NAME")
    user: str = Field(default="tahoe", env="DATABASE_USER")
    password: str = Field(default="tahoe", env="DATABASE_PASSWORD")
    
    @property
    def url(self) -> str:
        """Generate database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    class Config:
        env_prefix = ""


class RedisConfig(BaseSettings):
    """Redis configuration."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    @property
    def url(self) -> str:
        """Generate Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_prefix = ""


class ADKConfig(BaseSettings):
    """Google ADK configuration."""
    
    api_key: str = Field(default="", env="GEMINI_API_KEY")
    default_model: str = Field(default="gemini-2.0-flash", env="ADK_DEFAULT_MODEL")
    max_retries: int = Field(default=3, env="ADK_MAX_RETRIES")
    timeout: int = Field(default=30, env="ADK_TIMEOUT")
    
    @validator("api_key", pre=True)
    def validate_api_key(cls, v):
        # Handle missing API key gracefully in development
        if not v or v == "your-api-key-here":
            if IS_PRODUCTION:
                raise ValueError("GEMINI_API_KEY must be set in production")
            else:
                print("⚠ GEMINI_API_KEY not set - some features may not work")
                return "dev-placeholder-key"  # Return placeholder for development
        return v
    
    class Config:
        env_prefix = ""


class AgentEngineConfig(BaseSettings):
    """Agent Engine service configuration."""
    
    host: str = Field(default="0.0.0.0", env="AGENT_ENGINE_HOST")
    port: int = Field(default=8001, env="AGENT_ENGINE_PORT")
    log_level: str = Field(default="INFO", env="AGENT_ENGINE_LOG_LEVEL")
    workers: int = Field(default=1, env="AGENT_ENGINE_WORKERS")
    
    # Service metadata
    name: str = "agent-engine"
    title: str = "Tahoe Agent Engine"
    description: str = "Universal agent orchestration platform"
    version: str = "0.1.0"
    
    class Config:
        env_prefix = ""


class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if IS_PRODUCTION and v == "dev-secret-key":
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        return v
    
    class Config:
        env_prefix = ""


class ObservabilityConfig(BaseSettings):
    """Observability and monitoring configuration."""
    
    # Logging
    log_format: str = Field(default="json" if IS_PRODUCTION else "text", env="LOG_FORMAT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Metrics
    metrics_enabled: bool = Field(default=IS_PRODUCTION, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Tracing
    tracing_enabled: bool = Field(default=IS_PRODUCTION, env="TRACING_ENABLED")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    class Config:
        env_prefix = ""


class TahoeConfig(BaseSettings):
    """Main configuration class that combines all config sections."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=IS_DEVELOPMENT, env="DEBUG")
    
    # Service configurations
    @property
    def database(self) -> DatabaseConfig:
        if not hasattr(self, '_database'):
            self._database = DatabaseConfig()
        return self._database
    
    @property
    def redis(self) -> RedisConfig:
        if not hasattr(self, '_redis'):
            self._redis = RedisConfig()
        return self._redis
    
    @property
    def adk(self) -> ADKConfig:
        if not hasattr(self, '_adk'):
            self._adk = ADKConfig()
        return self._adk
    
    @property
    def agent_engine(self) -> AgentEngineConfig:
        if not hasattr(self, '_agent_engine'):
            self._agent_engine = AgentEngineConfig()
        return self._agent_engine
    
    @property
    def security(self) -> SecurityConfig:
        if not hasattr(self, '_security'):
            self._security = SecurityConfig()
        return self._security
    
    @property
    def observability(self) -> ObservabilityConfig:
        if not hasattr(self, '_observability'):
            self._observability = ObservabilityConfig()
        return self._observability
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Validate configuration for the current environment."""
        errors = []
        
        # Production validations
        if IS_PRODUCTION:
            if not self.adk.api_key or self.adk.api_key == "your-api-key-here":
                errors.append("GEMINI_API_KEY must be set in production")
            
            if self.security.secret_key == "dev-secret-key":
                errors.append("SECRET_KEY must be set to a secure value in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (for debugging/logging)."""
        config_dict = self.dict()
        
        # Mask sensitive values
        if "api_key" in str(config_dict):
            config_dict["adk"]["api_key"] = "***masked***"
        if "password" in str(config_dict):
            config_dict["database"]["password"] = "***masked***"
            if config_dict["redis"]["password"]:
                config_dict["redis"]["password"] = "***masked***"
        if "secret_key" in str(config_dict):
            config_dict["security"]["secret_key"] = "***masked***"
        
        return config_dict
    
    class Config:
        env_prefix = ""


# Global configuration instance
settings = TahoeConfig()


def get_settings() -> TahoeConfig:
    """Get the global settings instance."""
    return settings


def reload_settings() -> TahoeConfig:
    """Reload settings (useful for testing)."""
    global settings
    load_environment_config()
    settings = TahoeConfig()
    return settings


# Configuration validation on import
try:
    print(f"✓ Configuration loaded for environment: {settings.environment}")
    if settings.is_development:
        print(f"  - Agent Engine: http://{settings.agent_engine.host}:{settings.agent_engine.port}")
        print(f"  - Database: {settings.database.host}:{settings.database.port}")
        print(f"  - Redis: {settings.redis.host}:{settings.redis.port}")
        print(f"  - ADK Model: {settings.adk.default_model}")
except Exception as e:
    print(f"✗ Configuration error: {e}")
    if IS_PRODUCTION:
        # Fail fast in production
        sys.exit(1)
    else:
        print("  Continuing in development mode...")