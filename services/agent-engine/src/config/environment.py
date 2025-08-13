# services/agent-engine/src/config/environment.py
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class EnvironmentConfig:
    """Hierarchical environment configuration loader."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration in hierarchy: base -> environment -> runtime."""
        # 1. Load base .env file
        base_env = Path.cwd() / ".env"
        if base_env.exists():
            load_dotenv(base_env)
        
        # 2. Load environment-specific overrides
        env_file = Path.cwd() / "config" / f"{self.environment}.env"
        if env_file.exists():
            load_dotenv(env_file, override=True)
        
        # 3. Collect all configuration
        self.config = {
            # Database configuration
            "DATABASE_HOST": os.getenv("DATABASE_HOST", "localhost"),
            "DATABASE_PORT": os.getenv("DATABASE_PORT", "5432"),
            "DATABASE_NAME": os.getenv("DATABASE_NAME", "tahoe"),
            "DATABASE_USER": os.getenv("DATABASE_USER", "tahoe"),
            "DATABASE_PASSWORD": os.getenv("DATABASE_PASSWORD", "tahoe123"),
            
            # Service-specific configuration
            "AGENT_ENGINE_PORT": os.getenv("AGENT_ENGINE_PORT", "8001"),
            "AGENT_ENGINE_LOG_LEVEL": os.getenv("AGENT_ENGINE_LOG_LEVEL", "INFO"),
            "AGENT_ENGINE_DB_SCHEMA": os.getenv("AGENT_ENGINE_DB_SCHEMA", "agent_engine"),
            "AGENT_ENGINE_REDIS_NAMESPACE": os.getenv("AGENT_ENGINE_REDIS_NAMESPACE", "agent:"),
            
            # Redis configuration
            "REDIS_HOST": os.getenv("REDIS_HOST", "localhost"),
            "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
            
            # ADK configuration
            "ADK_SESSION_SERVICE": os.getenv("ADK_SESSION_SERVICE", "memory"),
            "ADK_DEFAULT_MODEL": os.getenv("ADK_DEFAULT_MODEL", "gemini-2.0-flash"),
            "ADK_TEMPERATURE": float(os.getenv("ADK_TEMPERATURE", "0.2")),
            "ADK_MAX_TOKENS": int(os.getenv("ADK_MAX_TOKENS", "8192")),
            
            # API Keys (sensitive)
            "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_database_url(self) -> str:
        """Build PostgreSQL connection URL with schema."""
        schema = self.config["AGENT_ENGINE_DB_SCHEMA"]
        return (
            f"postgresql://{self.config['DATABASE_USER']}:"
            f"{self.config['DATABASE_PASSWORD']}@"
            f"{self.config['DATABASE_HOST']}:"
            f"{self.config['DATABASE_PORT']}/"
            f"{self.config['DATABASE_NAME']}?schema={schema}"
        )
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration (excluding sensitive keys)."""
        safe_config = self.config.copy()
        # Remove sensitive keys
        sensitive_keys = ["GEMINI_API_KEY", "DATABASE_PASSWORD"]
        for key in sensitive_keys:
            if key in safe_config:
                safe_config[key] = "***MASKED***"
        return safe_config
    
    def validate_required_config(self) -> Dict[str, Any]:
        """Validate that required configuration is present."""
        required_keys = {
            "production": ["GEMINI_API_KEY", "DATABASE_HOST", "DATABASE_PASSWORD"],
            "staging": ["GEMINI_API_KEY", "DATABASE_HOST"],
            "development": []  # More lenient for development
        }
        
        missing_keys = []
        env_required = required_keys.get(self.environment, [])
        
        for key in env_required:
            if not self.config.get(key):
                missing_keys.append(key)
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys,
            "environment": self.environment
        }

# Global config instance
config = EnvironmentConfig()

def load_config() -> EnvironmentConfig:
    """Get configuration instance."""
    return config

def get_session_backend_config() -> Dict[str, Any]:
    """Get session backend configuration."""
    return {
        "backend": config.get("ADK_SESSION_SERVICE"),
        "redis_host": config.get("REDIS_HOST"),
        "redis_port": config.get("REDIS_PORT"),
        "redis_namespace": config.get("AGENT_ENGINE_REDIS_NAMESPACE"),
    }

def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return {
        "host": config.get("DATABASE_HOST"),
        "port": config.get("DATABASE_PORT"),
        "name": config.get("DATABASE_NAME"),
        "user": config.get("DATABASE_USER"),
        "schema": config.get("AGENT_ENGINE_DB_SCHEMA"),
        "url": config.get_database_url()
    }