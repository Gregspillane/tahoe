"""
Configuration API Endpoints

Provides REST API for configuration management:
- Get current configuration
- Reload configuration
- Validate configuration
- Get specific configuration values
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, Optional
import logging

from ..core.configuration import (
    get_config,
    reload_config,
    get_config_value,
    validate_config,
    _config_loader,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["Configuration"])


@router.get("/")
async def get_configuration(
    show_sensitive: bool = Query(
        False, description="Show sensitive values (use with caution)"
    ),
) -> Dict[str, Any]:
    """
    Get current configuration.

    - **show_sensitive**: If true, shows sensitive values like API keys (default: false)
    """
    try:
        config = get_config()
        return config.to_dict(mask_sensitive=not show_sensitive)
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.post("/reload")
async def reload_configuration() -> Dict[str, Any]:
    """
    Reload configuration from all sources.

    This will re-read:
    - Base .env file
    - Environment-specific overrides
    - Runtime specification overrides
    """
    try:
        config = reload_config()
        logger.info(f"Configuration reloaded for environment: {config.environment}")

        return {
            "status": "reloaded",
            "environment": config.environment,
            "timestamp": config.dict().get("timestamp", "unknown"),
            "message": "Configuration successfully reloaded from all sources",
        }
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(
            status_code=500, detail=f"Configuration reload error: {str(e)}"
        )


@router.get("/validate")
async def validate_configuration() -> Dict[str, Any]:
    """
    Validate current configuration.

    Returns validation results including:
    - Environment-specific validation checks
    - Required setting validation
    - Warning for development issues
    """
    try:
        validation_result = validate_config()

        # Log validation issues
        if validation_result["errors"]:
            logger.error(
                f"Configuration validation errors: {validation_result['errors']}"
            )
        if validation_result["warnings"]:
            logger.warning(
                f"Configuration validation warnings: {validation_result['warnings']}"
            )

        return validation_result
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        raise HTTPException(
            status_code=500, detail=f"Configuration validation error: {str(e)}"
        )


@router.get("/value/{key}")
async def get_configuration_value(
    key: str,
    default: Optional[str] = Query(None, description="Default value if key not found"),
) -> Dict[str, Any]:
    """
    Get specific configuration value by key.

    - **key**: Configuration key (supports nested keys like 'database.host')
    - **default**: Default value to return if key not found

    Examples:
    - `/config/value/environment`
    - `/config/value/database.host`
    - `/config/value/adk.default_model`
    """
    try:
        value = get_config_value(key, default)

        if value is None and default is None:
            raise HTTPException(
                status_code=404, detail=f"Configuration key '{key}' not found"
            )

        return {
            "key": key,
            "value": value,
            "default_used": value == default and default is not None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting configuration value '{key}': {e}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


@router.get("/environment")
async def get_environment_info() -> Dict[str, Any]:
    """
    Get environment information and configuration sources.

    Returns information about:
    - Current environment
    - Configuration file locations
    - Runtime override status
    """
    try:
        config = get_config()

        # Get configuration sources info
        base_dir = _config_loader.base_dir
        env_file = base_dir / "config" / f"{config.environment}.env"
        specs_dir = base_dir / "specs" / "config"

        # Count runtime overrides
        runtime_overrides = 0
        if specs_dir.exists():
            runtime_overrides = len(list(specs_dir.glob("*.yaml")))

        return {
            "environment": config.environment,
            "is_development": config.is_development,
            "is_staging": config.is_staging,
            "is_production": config.is_production,
            "base_dir": str(base_dir),
            "environment_file": str(env_file),
            "environment_file_exists": env_file.exists(),
            "runtime_overrides_dir": str(specs_dir),
            "runtime_overrides_count": runtime_overrides,
            "service_info": {
                "name": config.service_name,
                "version": config.version,
                "host": config.host,
                "port": config.port,
            },
        }
    except Exception as e:
        logger.error(f"Error getting environment info: {e}")
        raise HTTPException(status_code=500, detail=f"Environment info error: {str(e)}")


@router.get("/sections")
async def get_configuration_sections() -> Dict[str, Any]:
    """
    Get overview of all configuration sections.

    Returns summary of each configuration section without sensitive values.
    """
    try:
        config = get_config()

        return {
            "agent_engine": {
                "service_name": config.service_name,
                "host": config.host,
                "port": config.port,
                "environment": config.environment,
                "max_concurrent_executions": config.max_concurrent_executions,
            },
            "database": {
                "host": config.database.host,
                "port": config.database.port,
                "database_schema": config.database.database_schema,
                "max_connections": config.database.max_connections,
            },
            "redis": {
                "host": config.redis.host,
                "port": config.redis.port,
                "db": config.redis.db,
                "max_connections": config.redis.max_connections,
            },
            "adk": {
                "default_model": config.adk.default_model,
                "session_service": config.adk.session_service,
                "temperature": config.adk.temperature,
                "max_tokens": config.adk.max_tokens,
                "timeout": config.adk.timeout,
            },
            "security": {
                "cors_origins": config.security.cors_origins,
                "rate_limit_per_minute": config.security.rate_limit_per_minute,
                "session_expire_hours": config.security.session_expire_hours,
            },
            "observability": {
                "log_level": config.observability.log_level,
                "log_format": config.observability.log_format,
                "enable_metrics": config.observability.enable_metrics,
                "enable_tracing": config.observability.enable_tracing,
            },
        }
    except Exception as e:
        logger.error(f"Error getting configuration sections: {e}")
        raise HTTPException(
            status_code=500, detail=f"Configuration sections error: {str(e)}"
        )


@router.get("/health")
async def configuration_health() -> Dict[str, Any]:
    """
    Check configuration health and report issues.

    Returns health status of configuration system.
    """
    try:
        validation_result = validate_config()
        config = get_config()

        # Check configuration health
        health_status = "healthy"
        if validation_result["errors"]:
            health_status = "unhealthy"
        elif validation_result["warnings"]:
            health_status = "warning"

        return {
            "status": health_status,
            "environment": config.environment,
            "validation": validation_result,
            "checks": {
                "base_config_loaded": True,
                "environment_config_available": True,
                "runtime_overrides_applied": len(_config_loader.config_cache) > 0,
                "sensitive_values_present": bool(
                    config.adk.gemini_api_key
                    and not config.adk.gemini_api_key.startswith("CHANGE_THIS_")
                ),
            },
        }
    except Exception as e:
        logger.error(f"Error checking configuration health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checks": {
                "base_config_loaded": False,
                "environment_config_available": False,
                "runtime_overrides_applied": False,
                "sensitive_values_present": False,
            },
        }
