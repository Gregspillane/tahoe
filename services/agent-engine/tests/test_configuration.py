"""
Tests for Configuration System

Test suite covering:
- Configuration hierarchy loading
- Environment-specific overrides
- Redis namespace functionality
- Database schema configuration
- Runtime specification overrides
- Service discovery URLs
- Sensitive value masking
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path

from ..src.core.configuration import ConfigurationLoader, get_config, reload_config
from ..src.models.configuration import AgentEngineConfig, DatabaseConfig, RedisConfig, ADKConfig


class TestConfigurationModels:
    """Test configuration model validation and functionality."""
    
    def test_database_config_schema_url(self):
        """Test database URL generation with schema."""
        db_config = DatabaseConfig(
            host="localhost",
            port=5432,
            user="tahoe",
            password="tahoe123",
            schema="agent_engine"
        )
        
        expected_url = "postgresql://tahoe:tahoe123@localhost:5432/postgres?schema=agent_engine"
        assert db_config.url == expected_url
        assert "schema=agent_engine" in db_config.url
    
    def test_redis_namespace_functionality(self):
        """Test Redis namespace key generation."""
        redis_config = RedisConfig(namespace="agent:")
        
        # Test key namespacing
        key = redis_config.get_key("session:123")
        assert key == "agent:session:123"
        
        key = redis_config.get_key("cache:data")
        assert key == "agent:cache:data"
    
    def test_service_discovery_urls(self):
        """Test service URL generation based on environment."""
        config = AgentEngineConfig()
        
        # Development environment
        config.environment = "development"
        assert config.get_service_url("auth") == "http://localhost:8002"
        assert config.get_service_url("billing") == "http://localhost:8003"
        
        # Staging environment
        config.environment = "staging"
        assert config.get_service_url("auth") == "https://auth.staging.tahoe.com"
        assert config.get_service_url("billing") == "https://billing.staging.tahoe.com"
        
        # Production environment
        config.environment = "production"
        assert config.get_service_url("auth") == "https://auth.tahoe.com"
        assert config.get_service_url("billing") == "https://billing.tahoe.com"
    
    def test_adk_config_validation(self):
        """Test ADK configuration validation."""
        # Test valid configuration
        adk_config = ADKConfig(gemini_api_key="valid-key")
        assert adk_config.gemini_api_key == "valid-key"
        assert adk_config.default_model == "gemini-2.5-flash-lite"
        
        # Test session service validation
        with pytest.raises(ValueError, match="Session service must be one of"):
            ADKConfig(session_service="invalid")


class TestConfigurationLoader:
    """Test configuration loader functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create test directory structure
        (self.test_path / "config").mkdir()
        (self.test_path / "services" / "agent-engine" / "specs" / "config").mkdir(parents=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_hierarchy_loading(self):
        """Test configuration hierarchy loading."""
        # Create base .env file
        base_env = self.test_path / ".env"
        base_env.write_text("""
ENVIRONMENT=development
AGENT_ENGINE_PORT=8001
AGENT_ENGINE_DB_SCHEMA=agent_engine
AGENT_ENGINE_REDIS_NAMESPACE=agent:
DATABASE_HOST=localhost
REDIS_HOST=localhost
GEMINI_API_KEY=test-key
""")
        
        loader = ConfigurationLoader(str(self.test_path))
        config = loader.load()
        
        assert config.environment == "development"
        assert config.port == 8001
        assert config.database.schema == "agent_engine"
        assert config.redis.namespace == "agent:"
    
    def test_environment_override(self):
        """Test environment-specific overrides."""
        # Create base .env
        base_env = self.test_path / ".env"
        base_env.write_text("""
ENVIRONMENT=staging
AGENT_ENGINE_LOG_LEVEL=INFO
DATABASE_HOST=localhost
GEMINI_API_KEY=test-key
""")
        
        # Create staging override
        staging_env = self.test_path / "config" / "staging.env"
        staging_env.write_text("""
AGENT_ENGINE_LOG_LEVEL=DEBUG
DATABASE_HOST=staging-db.internal
""")
        
        with patch.dict(os.environ, {"ENVIRONMENT": "staging"}):
            loader = ConfigurationLoader(str(self.test_path))
            config = loader.load()
            
            assert config.environment == "staging"
            # Override should be applied
            assert config.database.host == "staging-db.internal"
    
    def test_runtime_spec_loading(self):
        """Test runtime specification override loading."""
        # Create base config
        base_env = self.test_path / ".env"
        base_env.write_text("""
ENVIRONMENT=development
AGENT_ENGINE_MAX_CONCURRENT=10
GEMINI_API_KEY=test-key
""")
        
        # Create runtime override spec
        spec_file = self.test_path / "services" / "agent-engine" / "specs" / "config" / "test-override.yaml"
        spec_content = {
            "apiVersion": "agent-engine/v1",
            "kind": "ConfigOverride",
            "metadata": {
                "name": "test-override"
            },
            "spec": {
                "development": {
                    "max_concurrent_executions": 5,
                    "cache_ttl": 7200
                },
                "global": {
                    "enable_audit": True
                }
            }
        }
        
        with open(spec_file, 'w') as f:
            yaml.dump(spec_content, f)
        
        loader = ConfigurationLoader(str(self.test_path))
        config = loader.load()
        
        # Runtime overrides should be applied
        assert config.max_concurrent_executions == 5
        assert config.cache_ttl == 7200
        assert config.enable_audit == True
    
    def test_sensitive_masking(self):
        """Test sensitive value masking."""
        base_env = self.test_path / ".env"
        base_env.write_text("""
ENVIRONMENT=development
GEMINI_API_KEY=secret-api-key
DATABASE_PASSWORD=secret-password
REDIS_PASSWORD=secret-redis-pass
""")
        
        loader = ConfigurationLoader(str(self.test_path))
        loader.load()
        config_dict = loader.to_dict(mask_sensitive=True)
        
        assert config_dict["adk"]["gemini_api_key"] == "***MASKED***"
        assert config_dict["database"]["password"] == "***MASKED***"
        if config_dict["redis"]["password"]:
            assert config_dict["redis"]["password"] == "***MASKED***"
    
    def test_nested_key_access(self):
        """Test nested configuration key access."""
        base_env = self.test_path / ".env"
        base_env.write_text("""
ENVIRONMENT=development
DATABASE_HOST=test-db
REDIS_HOST=test-redis
GEMINI_API_KEY=test-key
""")
        
        loader = ConfigurationLoader(str(self.test_path))
        loader.load()
        
        # Test nested key access
        assert loader.get("database.host") == "test-db"
        assert loader.get("redis.host") == "test-redis"
        assert loader.get("environment") == "development"
        assert loader.get("nonexistent.key", "default") == "default"


class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "development",
        "AGENT_ENGINE_PORT": "8001",
        "AGENT_ENGINE_DB_SCHEMA": "agent_engine",
        "AGENT_ENGINE_REDIS_NAMESPACE": "agent:",
        "DATABASE_HOST": "localhost",
        "REDIS_HOST": "localhost",
        "GEMINI_API_KEY": "test-key"
    })
    def test_global_config_functions(self):
        """Test global configuration access functions."""
        config = get_config()
        
        assert config.environment == "development"
        assert config.port == 8001
        assert config.database.schema == "agent_engine"
        assert config.redis.namespace == "agent:"
        
        # Test reload
        reloaded_config = reload_config()
        assert reloaded_config.environment == "development"
    
    def test_configuration_validation(self):
        """Test configuration validation rules."""
        # Test invalid environment
        with pytest.raises(ValueError, match="Environment must be one of"):
            AgentEngineConfig(environment="invalid")
        
        # Test invalid port
        with pytest.raises(ValueError, match="Service port must be between"):
            AgentEngineConfig(port=70000)
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "development",
        "GEMINI_API_KEY": "test-key",
        "DATABASE_HOST": "localhost",
        "REDIS_HOST": "localhost"
    })
    def test_complete_configuration_flow(self):
        """Test complete configuration loading and usage flow."""
        # Load configuration
        config = get_config()
        
        # Verify all components accessible
        assert config.database.url.startswith("postgresql://")
        assert "schema=" in config.database.url
        assert config.redis.get_key("test") == "agent:test"
        assert config.get_service_url("auth") == "http://localhost:8002"
        
        # Test configuration dictionary export
        config_dict = config.to_dict(mask_sensitive=True)
        assert "database" in config_dict
        assert "redis" in config_dict
        assert "adk" in config_dict
        assert config_dict["adk"]["gemini_api_key"] == "***MASKED***"


class TestEnvironmentSpecificBehavior:
    """Test environment-specific configuration behavior."""
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "GEMINI_API_KEY": "prod-key",
        "DATABASE_HOST": "prod-db.internal",
        "REDIS_HOST": "prod-redis.internal"
    })
    def test_production_configuration(self):
        """Test production-specific configuration."""
        config = get_config()
        
        assert config.environment == "production"
        assert config.is_production == True
        assert config.is_development == False
        assert config.get_service_url("auth") == "https://auth.tahoe.com"
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "staging",
        "GEMINI_API_KEY": "staging-key",
        "DATABASE_HOST": "staging-db.internal",
        "REDIS_HOST": "staging-redis.internal"
    })
    def test_staging_configuration(self):
        """Test staging-specific configuration."""
        config = get_config()
        
        assert config.environment == "staging"
        assert config.is_staging == True
        assert config.is_production == False
        assert config.get_service_url("auth") == "https://auth.staging.tahoe.com"


# Performance tests
class TestConfigurationPerformance:
    """Test configuration system performance."""
    
    def test_config_loading_performance(self):
        """Test configuration loading is reasonably fast."""
        import time
        
        start_time = time.time()
        for _ in range(100):
            config = get_config()
        end_time = time.time()
        
        # Should load 100 configs in less than 1 second
        assert (end_time - start_time) < 1.0
    
    def test_nested_key_access_performance(self):
        """Test nested key access performance."""
        import time
        
        config = get_config()
        loader = ConfigurationLoader()
        loader.load()
        
        start_time = time.time()
        for _ in range(1000):
            loader.get("database.host")
            loader.get("redis.namespace")
            loader.get("adk.default_model")
        end_time = time.time()
        
        # Should access 3000 nested keys in less than 0.1 seconds
        assert (end_time - start_time) < 0.1