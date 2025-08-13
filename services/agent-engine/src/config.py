from pydantic_settings import BaseSettings
from pydantic import computed_field
from typing import Optional, List


class ServiceConfig(BaseSettings):
    SERVICE_NAME: str = "agent-engine"
    SERVICE_VERSION: str = "0.1.0"
    
    # Environment awareness (development, staging, production)
    ENVIRONMENT: str = "development"
    
    # Service configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DOMAIN: str = "yourdomain.com"
    
    # Database configuration
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5435
    DATABASE_NAME: str = "tahoe"
    DATABASE_USER: str = "tahoe"
    DATABASE_PASSWORD: str = "tahoe"
    DATABASE_SCHEMA: str = "agent_engine"
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6382
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PREFIX: str = "agent-engine:"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS origins
    CORS_ALLOWED_ORIGINS: Optional[List[str]] = None
    
    # Service authentication
    SERVICE_TO_SERVICE_TOKEN: Optional[str] = None
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @computed_field
    @property
    def SERVICE_URL(self) -> str:
        """Compute service URL based on environment"""
        if self.ENVIRONMENT == "development":
            return f"http://localhost:{self.PORT}"
        elif self.ENVIRONMENT == "staging":
            return f"https://agent.staging.{self.DOMAIN}"
        else:  # production
            return f"https://agent.{self.DOMAIN}"
    
    @computed_field
    @property
    def DEBUG(self) -> bool:
        """Enable debug mode for development"""
        return self.ENVIRONMENT == "development"
    
    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins"""
        if self.CORS_ALLOWED_ORIGINS:
            return self.CORS_ALLOWED_ORIGINS
        # Default to permissive in development
        return ["*"] if self.ENVIRONMENT == "development" else []
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = ServiceConfig()