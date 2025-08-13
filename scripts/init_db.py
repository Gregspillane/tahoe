#!/usr/bin/env python3
"""Database initialization script with schema creation."""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services" / "agent-engine"))

from prisma import Prisma
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Try to import config, fallback to environment variables
try:
    from src.config.environment import config
except ImportError:
    # Fallback to direct environment access
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    class SimpleConfig:
        def get(self, key, default=None):
            return os.getenv(key, default)
    
    config = SimpleConfig()


async def create_service_schemas():
    """Create service-specific database schemas."""
    print("Creating service schemas...")
    
    # Connect directly to PostgreSQL to create schemas
    conn = psycopg2.connect(
        host=config.get("DATABASE_HOST"),
        port=config.get("DATABASE_PORT"),
        database=config.get("DATABASE_NAME"),
        user=config.get("DATABASE_USER"),
        password=config.get("DATABASE_PASSWORD")
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Create schemas for each service
    schemas = ["agent_engine", "auth", "billing"]  # Service isolation
    for schema in schemas:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        print(f"✓ Schema {schema} created or already exists")
    
    cursor.close()
    conn.close()
    print("✓ Service schemas ready")


async def generate_prisma_client():
    """Generate Prisma client."""
    print("Generating Prisma client...")
    import subprocess
    
    # Change to infrastructure directory for Prisma commands
    infrastructure_dir = Path(__file__).parent.parent / "services" / "infrastructure"
    original_dir = os.getcwd()
    
    try:
        os.chdir(infrastructure_dir)
        result = subprocess.run(["prisma", "generate"], check=True, capture_output=True, text=True)
        print("✓ Prisma client generated successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to generate Prisma client: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    finally:
        os.chdir(original_dir)


async def run_migrations():
    """Run Prisma migrations."""
    print("Running Prisma migrations...")
    import subprocess
    
    # Change to infrastructure directory for Prisma commands
    infrastructure_dir = Path(__file__).parent.parent / "services" / "infrastructure"
    original_dir = os.getcwd()
    
    try:
        os.chdir(infrastructure_dir)
        result = subprocess.run(["prisma", "migrate", "deploy"], check=True, capture_output=True, text=True)
        print("✓ Migrations applied successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to run migrations: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    finally:
        os.chdir(original_dir)


async def seed_initial_data(prisma: Prisma):
    """Seed initial configuration data."""
    print("Seeding initial data...")
    
    # Check if already seeded
    existing = await prisma.configurationversion.find_first()
    if existing:
        print("✓ Database already seeded")
        return
    
    # Add default model configuration
    await prisma.configurationversion.create(
        data={
            "type": "model",
            "name": "default",
            "version": "1.0.0",
            "specification": {
                "provider": "google",
                "model": config.get("ADK_DEFAULT_MODEL", "gemini-2.0-flash"),
                "parameters": {
                    "temperature": config.get("ADK_TEMPERATURE", 0.2),
                    "max_tokens": config.get("ADK_MAX_TOKENS", 8192)
                }
            },
            "created_by": "system"
        }
    )
    
    # Add default session backend configuration
    await prisma.configurationversion.create(
        data={
            "type": "session",
            "name": "backend-config",
            "version": "1.0.0",
            "specification": {
                "default_backend": config.get("ADK_SESSION_SERVICE", "memory"),
                "available_backends": ["memory", "redis", "vertex"],
                "redis_config": {
                    "host": config.get("REDIS_HOST", "localhost"),
                    "port": config.get("REDIS_PORT", 6379),
                    "namespace": config.get("AGENT_ENGINE_REDIS_NAMESPACE", "agent:")
                }
            },
            "created_by": "system"
        }
    )
    
    print("✓ Initial data seeded")


async def test_connection(prisma: Prisma):
    """Test database connection."""
    print("Testing database connection...")
    
    try:
        # Test basic query
        count = await prisma.session.count()
        print(f"✓ Database connection successful (sessions: {count})")
        
        # Test schema isolation by checking a simple query
        tools_count = await prisma.toolregistry.count()
        configs_count = await prisma.configurationversion.count()
        print(f"✓ Schema access working (tools: {tools_count}, configs: {configs_count})")
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        raise


async def init_database():
    """Initialize database with schema and migrations."""
    print("🚀 Initializing Tahoe database...")
    print(f"Environment: {config.get('ENVIRONMENT', 'development')}")
    print(f"Database: {config.get('DATABASE_NAME')}@{config.get('DATABASE_HOST')}")
    print(f"Schema: {config.get('AGENT_ENGINE_DB_SCHEMA')}")
    print()
    
    try:
        # Step 1: Create service schemas
        await create_service_schemas()
        
        # Step 2: Generate Prisma client
        await generate_prisma_client()
        
        # Step 3: Run migrations
        await run_migrations()
        
        # Step 4: Test connection and seed data
        prisma = Prisma()
        await prisma.connect()
        
        # Step 5: Seed initial data
        await seed_initial_data(prisma)
        
        # Step 6: Test everything works
        await test_connection(prisma)
        
        await prisma.disconnect()
        
        print()
        print("✅ Database initialized successfully!")
        print("   • Service schemas created")
        print("   • Prisma client generated")
        print("   • Migrations applied")
        print("   • Initial data seeded")
        print("   • Connection verified")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())