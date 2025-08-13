from pydantic_settings import BaseSettings
from typing import Optional


class ServiceConfig(BaseSettings):
    SERVICE_NAME: str = "agent-engine"
    SERVICE_VERSION: str = "0.1.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/tahoe"
    DATABASE_SCHEMA: str = "agent_engine"
    
    REDIS_URL: str = "redis://redis:6379"
    REDIS_PREFIX: str = "agent-engine:"
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    LOG_LEVEL: str = "INFO"
    
    CORS_ORIGINS: list[str] = ["*"]
    
    SERVICE_TO_SERVICE_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = ServiceConfig()