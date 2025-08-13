"""
Configuration Management System for Tahoe Agent Engine

This module provides hierarchical configuration loading with:
- Base .env file configuration
- Environment-specific overrides
- Runtime specification support
- Dynamic configuration reloading
"""

from pathlib import Path
from typing import Dict, Any, Optional
import os
import json
import yaml
from dotenv import load_dotenv
import logging

from ..models.configuration import AgentEngineConfig

logger = logging.getLogger(__name__)


class ConfigurationLoader:
    """Hierarchical configuration loader with runtime support."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.getcwd())
        self.config_cache: Dict[str, Any] = {}
        self._config: Optional[AgentEngineConfig] = None
        
    def load(self) -> AgentEngineConfig:
        """Load configuration with hierarchy:
        1. Base .env file
        2. Environment-specific overrides
        3. Runtime specifications
        4. Create configuration object
        """
        logger.info("Loading hierarchical configuration...")
        
        # 1. Load base .env file
        base_env = self.base_dir / ".env"
        if base_env.exists():
            load_dotenv(base_env)
            logger.info(f"Loaded base configuration from {base_env}")
        else:
            logger.warning(f"Base .env file not found at {base_env}")
        
        # 2. Load environment-specific overrides
        environment = os.getenv("ENVIRONMENT", "development")
        env_file = self.base_dir / "config" / f"{environment}.env"
        if env_file.exists():
            load_dotenv(env_file, override=True)
            logger.info(f"Applied {environment} environment overrides from {env_file}")
        else:
            logger.info(f"No environment overrides found for {environment}")
        
        # 3. Create configuration object
        self._config = AgentEngineConfig()
        
        # 4. Load runtime specifications
        self._load_runtime_specs()
        
        logger.info(f"Configuration loaded successfully for environment: {environment}")
        return self._config
    
    def _load_runtime_specs(self):
        """Load runtime specification overrides from specs/config/ directory."""
        # CORRECTED: Enhanced implementation for ConfigOverride specs
        specs_dir = self.base_dir / "services" / "agent-engine" / "specs" / "config"
        if not specs_dir.exists():
            logger.info("No runtime specification overrides found")
            return
        
        for spec_file in specs_dir.glob("*.yaml"):
            try:
                with open(spec_file) as f:
                    spec = yaml.safe_load(f)
                    if spec and spec.get("kind") == "ConfigOverride":
                        self._apply_spec_overrides(spec)
                        logger.info(f"Applied runtime overrides from {spec_file.name}")
            except Exception as e:
                logger.error(f"Error loading spec {spec_file}: {e}")
    
    def _apply_spec_overrides(self, spec: Dict[str, Any]):
        """Apply specification overrides to configuration."""
        overrides = spec.get("spec", {})
        metadata = spec.get("metadata", {})
        environment = self._config.environment
        
        logger.info(f"Applying config overrides from {metadata.get('name', 'unknown')} for {environment}")
        
        # Apply environment-specific overrides if present
        env_overrides = overrides.get(environment, {})
        self._apply_overrides_to_config(env_overrides)
        
        # Apply global overrides
        global_overrides = overrides.get("global", {})
        self._apply_overrides_to_config(global_overrides)
    
    def _apply_overrides_to_config(self, overrides: Dict[str, Any]):
        """Apply override dictionary to configuration."""
        for key, value in overrides.items():
            try:
                # Handle nested configuration (e.g., "database.host")
                if "." in key:
                    parts = key.split(".")
                    target = self._config
                    for part in parts[:-1]:
                        if hasattr(target, part):
                            target = getattr(target, part)
                        else:
                            logger.warning(f"Config path not found: {key}")
                            break
                    else:
                        if hasattr(target, parts[-1]):
                            setattr(target, parts[-1], value)
                            logger.info(f"Override applied: {key} = {value}")
                        else:
                            logger.warning(f"Config attribute not found: {key}")
                elif hasattr(self._config, key):
                    setattr(self._config, key, value)
                    logger.info(f"Override applied: {key} = {value}")
                else:
                    logger.warning(f"Config attribute not found: {key}")
            except Exception as e:
                logger.error(f"Error applying override {key}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys)."""
        if not self._config:
            self.load()
        
        # Support nested keys (e.g., "database.host")
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def reload(self) -> AgentEngineConfig:
        """Reload configuration from all sources."""
        logger.info("Reloading configuration...")
        self.config_cache.clear()
        self._config = None
        return self.load()
    
    def to_dict(self, mask_sensitive: bool = True) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        if not self._config:
            self.load()
        
        config_dict = self._config.dict()
        
        if mask_sensitive:
            # Mask sensitive values
            if "adk" in config_dict and "api_key" in config_dict["adk"]:
                config_dict["adk"]["api_key"] = "***MASKED***"
            if "database" in config_dict and "password" in config_dict["database"]:
                config_dict["database"]["password"] = "***MASKED***"
            if "redis" in config_dict and config_dict["redis"].get("password"):
                config_dict["redis"]["password"] = "***MASKED***"
            if "security" in config_dict and "secret_key" in config_dict["security"]:
                config_dict["security"]["secret_key"] = "***MASKED***"
        
        return config_dict
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate configuration for current environment."""
        if not self._config:
            self.load()
        
        validation_result = {
            "valid": True,
            "environment": self._config.environment,
            "errors": [],
            "warnings": []
        }
        
        # Validate based on environment
        if self._config.is_production:
            # Production validations
            if not self._config.adk.gemini_api_key or self._config.adk.gemini_api_key.startswith("CHANGE_THIS_"):
                validation_result["errors"].append("GEMINI_API_KEY must be set in production")
            
            if self._config.security.secret_key == "dev-secret-key":
                validation_result["errors"].append("SECRET_KEY must be set to a secure value in production")
        
        elif self._config.is_development:
            # Development warnings
            if not self._config.adk.gemini_api_key or self._config.adk.gemini_api_key.startswith("CHANGE_THIS_"):
                validation_result["warnings"].append("GEMINI_API_KEY not set - some features may not work")
        
        validation_result["valid"] = len(validation_result["errors"]) == 0
        
        return validation_result


# Global configuration loader instance
_config_loader = ConfigurationLoader()


def get_config() -> AgentEngineConfig:
    """Get global configuration."""
    return _config_loader.load()


def reload_config() -> AgentEngineConfig:
    """Reload global configuration."""
    return _config_loader.reload()


def get_config_value(key: str, default: Any = None) -> Any:
    """Get specific configuration value by key."""
    return _config_loader.get(key, default)


def validate_config() -> Dict[str, Any]:
    """Validate current configuration."""
    return _config_loader.validate_environment()