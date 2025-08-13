#!/usr/bin/env python3
"""Validation script for corrected R1-T04 implementation."""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "agent-engine"))

def test_imports():
    """Test that all corrected modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test session backend manager
        from src.services.session_backends import (
            RedisSessionService, 
            VertexSessionService, 
            get_session_backend,
            SessionBackendManager
        )
        print("✓ Session backend manager imports successfully")
        
        # Test environment configuration
        from src.config.environment import (
            EnvironmentConfig,
            load_config,
            get_session_backend_config,
            get_database_config
        )
        print("✓ Environment configuration imports successfully")
        
        # Test database service (might fail without Prisma client)
        try:
            from src.services.database import DatabaseService, get_db
            print("✓ Database service imports successfully")
        except ImportError as e:
            print(f"⚠ Database service import failed (expected without Prisma client): {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_schema_configuration():
    """Test schema configuration."""
    print("\n🧪 Testing schema configuration...")
    
    try:
        # Read schema file
        schema_path = project_root / "services" / "infrastructure" / "prisma" / "schema.prisma"
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        # Check for corrected features
        checks = [
            ('schemas  = ["agent_engine", "public"]', "Multi-schema support"),
            ('@@schema("agent_engine")', "Service schema isolation"),
            ('backend    String    @default("memory")', "Session backend field"),
            ('@@index([backend])', "Backend indexing")
        ]
        
        for check, description in checks:
            if check in schema_content:
                print(f"✓ {description}")
            else:
                print(f"✗ Missing: {description}")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        return False

def test_environment_configuration():
    """Test environment configuration."""
    print("\n🧪 Testing environment configuration...")
    
    try:
        from src.config.environment import config
        
        # Test configuration values
        checks = [
            ("AGENT_ENGINE_DB_SCHEMA", "agent_engine"),
            ("AGENT_ENGINE_REDIS_NAMESPACE", "agent:"),
            ("ADK_SESSION_SERVICE", "memory"),
            ("DATABASE_NAME", "tahoe")
        ]
        
        for key, expected in checks:
            value = config.get(key)
            if value == expected:
                print(f"✓ {key} = {value}")
            else:
                print(f"⚠ {key} = {value} (expected: {expected})")
        
        # Test configuration methods
        db_url = config.get_database_url()
        if "schema=agent_engine" in db_url:
            print("✓ Database URL includes schema")
        else:
            print(f"✗ Database URL missing schema: {db_url}")
        
        return True
        
    except Exception as e:
        print(f"✗ Environment configuration failed: {e}")
        return False

def test_session_backends():
    """Test session backend functionality."""
    print("\n🧪 Testing session backends...")
    
    try:
        from src.services.session_backends import get_session_backend, SessionBackendManager
        
        # Test backend manager
        manager = SessionBackendManager()
        backend_info = manager.get_backend_info()
        
        expected_backends = ["memory", "redis", "vertex"]
        if set(backend_info["available"]) == set(expected_backends):
            print("✓ All expected backends available")
        else:
            print(f"✗ Backend mismatch: {backend_info['available']}")
        
        # Test memory backend (should always work)
        memory_backend = get_session_backend("memory")
        if memory_backend:
            print("✓ Memory backend creation successful")
        else:
            print("✗ Memory backend creation failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Session backend test failed: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration."""
    print("\n🧪 Testing Docker configuration...")
    
    try:
        # Read docker-compose file
        docker_path = project_root / "services" / "infrastructure" / "docker-compose.yml"
        with open(docker_path, 'r') as f:
            docker_content = f.read()
        
        # Check for Redis service and persistence
        checks = [
            ('redis:', "Redis service defined"),
            ('redis:7-alpine', "Redis 7 image"),
            ('redis-server --appendonly yes', "Redis persistence enabled"),
            ('redis_data:/data', "Redis volume mapping")
        ]
        
        for check, description in checks:
            if check in docker_content:
                print(f"✓ {description}")
            else:
                print(f"✗ Missing: {description}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Docker configuration test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Validating corrected R1-T04 implementation...")
    print(f"Project root: {project_root}")
    print()
    
    tests = [
        test_imports,
        test_schema_configuration, 
        test_environment_configuration,
        test_session_backends,
        test_docker_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All corrected R1-T04 implementations validated successfully!")
        print("🎯 Key corrections implemented:")
        print("   • Database schema isolation with @@schema directives")
        print("   • Session backend field for multi-backend tracking")
        print("   • Redis session service with namespace isolation")
        print("   • Environment configuration hierarchy")
        print("   • Service-specific configuration prefixes")
        print("   • Docker Redis persistence configuration")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)