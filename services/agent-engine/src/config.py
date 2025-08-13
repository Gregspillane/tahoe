from pydantic_settings import BaseSettings
from pydantic import computed_field, Field
from typing import Optional, List
import os
from pathlib import Path
from dotenv import load_dotenv

# Load centralized .env file from project root
project_root = Path(__file__).parent.parent.parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded configuration from: {env_file}")

# Also load environment-specific configs if they exist
environment = os.getenv("ENVIRONMENT", "development")
env_specific_file = project_root / "config" / f"{environment}.env"
if env_specific_file.exists():
    load_dotenv(env_specific_file, override=True)
    print(f"Loaded {environment} overrides from: {env_specific_file}")


class ServiceConfig(BaseSettings):
    SERVICE_NAME: str = "agent-engine"
    SERVICE_VERSION: str = "0.1.0"
    
    # Environment awareness (development, staging, production)
    ENVIRONMENT: str = "development"
    
    # Service configuration
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8001, alias="AGENT_ENGINE_PORT")
    DOMAIN: str = "yourdomain.com"
    
    # Database configuration (shared infrastructure)
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5435
    DATABASE_NAME: str = "tahoe"
    DATABASE_USER: str = "tahoe"
    DATABASE_PASSWORD: str  # Required from environment
    DATABASE_SCHEMA: str = Field(default="agent_engine", alias="AGENT_ENGINE_DATABASE_SCHEMA")
    
    # Redis configuration (shared infrastructure)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6382
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PREFIX: str = "agent-engine:"
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", alias="AGENT_ENGINE_LOG_LEVEL")
    
    # CORS origins
    CORS_ALLOWED_ORIGINS: Optional[List[str]] = None
    
    # Service authentication
    SERVICE_TO_SERVICE_TOKEN: Optional[str] = Field(default=None, alias="AGENT_ENGINE_SERVICE_TOKEN")
    
    # LLM Provider API Keys
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components with connection pooling"""
        base_url = f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        # Add connection pool parameters for Prisma
        return f"{base_url}?connection_limit=10&pool_timeout=30"
    
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
        # Load from centralized .env files in order of precedence
        env_file = [
            # Highest priority: environment-specific config
            f"../../config/{os.getenv('ENVIRONMENT', 'development')}.env",
            # Base configuration
            "../../.env"
        ]
        case_sensitive = True
        env_file_encoding = 'utf-8'


# Helper function to get project root
def get_project_root() -> Path:
    """Get the project root directory (tahoe/)"""
    return Path(__file__).parent.parent.parent.parent


# Update env_file paths to be absolute
def get_env_files() -> List[str]:
    """Get environment file paths relative to project root"""
    project_root = get_project_root()
    environment = os.getenv('ENVIRONMENT', 'development')
    
    return [
        str(project_root / f"config/{environment}.env"),
        str(project_root / ".env")
    ]


class ServiceConfigWithCentralizedEnv(ServiceConfig):
    """ServiceConfig that loads from centralized .env files"""
    
    class Config:
        # Don't use pydantic's env_file since we're using dotenv.load_dotenv above
        # This ensures we load from the centralized location
        env_file = None
        case_sensitive = True
        env_file_encoding = 'utf-8'
        # Allow reading from environment variables
        validate_default = True


# Create settings instance - will read from environment variables
# that were loaded by dotenv.load_dotenv() above
settings = ServiceConfigWithCentralizedEnv()