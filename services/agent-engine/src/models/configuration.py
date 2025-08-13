"""
Configuration Models for Tahoe Agent Engine

Pydantic models for all configuration sections with validation and type safety.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_DEVELOPMENT = ENVIRONMENT == "development"
IS_STAGING = ENVIRONMENT == "staging"
IS_PRODUCTION = ENVIRONMENT == "production"


def load_environment_config():
    """Load environment configuration based on deployment context."""
    if IS_DEVELOPMENT:
        # In development, load from root .env file
        root_env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
        if root_env_path.exists():
            load_dotenv(root_env_path)
    # In staging/production, rely on environment variables from Helm/Vault


# Load configuration on import
load_environment_config()


class DatabaseConfig(BaseSettings):
    """Database configuration with validation."""
    
    host: str = Field(default="localhost", env="DATABASE_HOST")
    port: int = Field(default=5432, env="DATABASE_PORT")
    user: str = Field(default="tahoe", env="DATABASE_USER")
    password: str = Field(default="tahoe123", env="DATABASE_PASSWORD")
    # CORRECTED: Use database_schema instead of separate database
    database_schema: str = Field(default="agent_engine", env="AGENT_ENGINE_DB_SCHEMA")
    
    # Connection pool settings
    min_connections: int = Field(default=1, env="DATABASE_MIN_CONNECTIONS")
    max_connections: int = Field(default=10, env="DATABASE_MAX_CONNECTIONS")
    connection_timeout: int = Field(default=30, env="DATABASE_CONNECTION_TIMEOUT")
    
    @property
    def url(self) -> str:
        """Generate database URL with schema for Prisma."""
        # CORRECTED: Connection uses postgres database with schema qualifier
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/postgres?schema={self.database_schema}"
    
    @validator("port")
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Database port must be between 1 and 65535")
        return v
    
    class Config:
        env_prefix = ""


class RedisConfig(BaseSettings):
    """Redis configuration for caching and sessions."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    # ADDED: Redis namespace for service isolation
    namespace: str = Field(default="agent:", env="AGENT_ENGINE_REDIS_NAMESPACE")
    
    # Connection settings
    max_connections: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=30, env="REDIS_SOCKET_TIMEOUT")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    
    @property
    def url(self) -> str:
        """Generate Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    def get_key(self, key: str) -> str:
        """Get namespaced Redis key for service isolation."""
        return f"{self.namespace}{key}"
    
    @validator("port")
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Redis port must be between 1 and 65535")
        return v
    
    @validator("db")
    def validate_db(cls, v):
        if not 0 <= v <= 15:
            raise ValueError("Redis DB must be between 0 and 15")
        return v
    
    class Config:
        env_prefix = ""


class ADKConfig(BaseSettings):
    """Google ADK configuration with model settings."""
    
    # API Configuration
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    
    # Model Configuration
    default_model: str = Field(default="gemini-2.5-flash-lite", env="ADK_DEFAULT_MODEL")
    fallback_models: List[str] = Field(
        default=["gemini-2.5-pro", "gemini-2.5-flash"], 
        env="ADK_FALLBACK_MODELS"
    )
    
    # Generation Parameters
    temperature: float = Field(default=0.2, env="ADK_TEMPERATURE")
    max_tokens: int = Field(default=8192, env="ADK_MAX_TOKENS")
    top_p: float = Field(default=0.95, env="ADK_TOP_P")
    top_k: int = Field(default=40, env="ADK_TOP_K")
    
    # Session Configuration
    session_service: str = Field(default="memory", env="ADK_SESSION_SERVICE")
    session_timeout: int = Field(default=3600, env="ADK_SESSION_TIMEOUT")
    
    # Reliability Configuration
    timeout: int = Field(default=300, env="ADK_TIMEOUT")
    retry_attempts: int = Field(default=3, env="ADK_RETRY_ATTEMPTS")
    retry_delay: int = Field(default=1, env="ADK_RETRY_DELAY")
    
    @validator("gemini_api_key")
    def validate_api_key(cls, v):
        if v.startswith("CHANGE_THIS_"):
            if IS_PRODUCTION:
                raise ValueError("API key not configured - update GEMINI_API_KEY")
            else:
                # Return placeholder for development
                return "dev-placeholder-key"
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @validator("session_service")
    def validate_session_service(cls, v):
        valid_services = ["memory", "redis", "vertex"]
        if v not in valid_services:
            raise ValueError(f"Session service must be one of: {valid_services}")
        return v
    
    class Config:
        env_prefix = ""


class SecurityConfig(BaseSettings):
    """Security configuration for authentication and authorization."""
    
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # API Security
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Session Security
    session_expire_hours: int = Field(default=24, env="SESSION_EXPIRE_HOURS")
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if IS_PRODUCTION and v == "dev-secret-key":
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        if IS_PRODUCTION and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_prefix = ""


class ObservabilityConfig(BaseSettings):
    """Observability and monitoring configuration."""
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json" if IS_PRODUCTION else "text", env="LOG_FORMAT")
    
    # Metrics
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Tracing
    enable_tracing: bool = Field(default=IS_PRODUCTION, env="ENABLE_TRACING")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # Health Checks
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = ""


class AgentEngineConfig(BaseSettings):
    """Main Agent Engine service configuration."""
    
    # Service Identity
    service_name: str = Field(default="agent-engine", env="AGENT_ENGINE_SERVICE_NAME")
    host: str = Field(default="0.0.0.0", env="AGENT_ENGINE_HOST")
    port: int = Field(default=8001, env="AGENT_ENGINE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # ADDED: Service discovery URLs for multi-service architecture
    auth_service_url: Optional[str] = Field(default=None, env="AUTH_SERVICE_URL")
    billing_service_url: Optional[str] = Field(default=None, env="BILLING_SERVICE_URL")
    
    # Service Metadata
    title: str = "Tahoe Agent Engine"
    description: str = "Universal agent orchestration platform"
    version: str = "0.1.0"
    
    # Performance Configuration
    max_concurrent_executions: int = Field(default=10, env="AGENT_ENGINE_MAX_CONCURRENT")
    cache_ttl: int = Field(default=3600, env="AGENT_ENGINE_CACHE_TTL")
    request_timeout: int = Field(default=300, env="AGENT_ENGINE_REQUEST_TIMEOUT")
    
    # Feature Flags
    enable_audit: bool = Field(default=True, env="AGENT_ENGINE_ENABLE_AUDIT")
    enable_streaming: bool = Field(default=True, env="AGENT_ENGINE_ENABLE_STREAMING")
    enable_validation: bool = Field(default=True, env="AGENT_ENGINE_ENABLE_VALIDATION")
    
    # Sub-configurations (lazy loaded)
    _database: Optional[DatabaseConfig] = None
    _redis: Optional[RedisConfig] = None
    _adk: Optional[ADKConfig] = None
    _security: Optional[SecurityConfig] = None
    _observability: Optional[ObservabilityConfig] = None
    
    @property
    def database(self) -> DatabaseConfig:
        if self._database is None:
            self._database = DatabaseConfig()
        return self._database
    
    @property
    def redis(self) -> RedisConfig:
        if self._redis is None:
            self._redis = RedisConfig()
        return self._redis
    
    @property
    def adk(self) -> ADKConfig:
        if self._adk is None:
            self._adk = ADKConfig()
        return self._adk
    
    @property
    def security(self) -> SecurityConfig:
        if self._security is None:
            self._security = SecurityConfig()
        return self._security
    
    @property
    def observability(self) -> ObservabilityConfig:
        if self._observability is None:
            self._observability = ObservabilityConfig()
        return self._observability
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_staging(self) -> bool:
        return self.environment == "staging"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @validator("port")
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Service port must be between 1 and 65535")
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v
    
    def get_service_url(self, service: str) -> str:
        """Get service URL based on environment for service discovery."""
        if self.environment == "development":
            ports = {"auth": 8002, "billing": 8003}
            return f"http://localhost:{ports.get(service, 8000)}"
        elif self.environment == "staging":
            return f"https://{service}.staging.tahoe.com"
        else:  # production
            return f"https://{service}.tahoe.com"
    
    def to_dict(self, mask_sensitive: bool = True) -> Dict[str, Any]:
        """Convert configuration to dictionary with optional sensitive masking."""
        config_dict = self.dict()
        
        # Add sub-configurations
        config_dict["database"] = self.database.dict()
        config_dict["redis"] = self.redis.dict()
        config_dict["adk"] = self.adk.dict()
        config_dict["security"] = self.security.dict()
        config_dict["observability"] = self.observability.dict()
        
        if mask_sensitive:
            # Mask sensitive values
            config_dict["adk"]["gemini_api_key"] = "***MASKED***"
            config_dict["database"]["password"] = "***MASKED***"
            if config_dict["redis"]["password"]:
                config_dict["redis"]["password"] = "***MASKED***"
            config_dict["security"]["secret_key"] = "***MASKED***"
        
        return config_dict
    
    class Config:
        env_prefix = ""