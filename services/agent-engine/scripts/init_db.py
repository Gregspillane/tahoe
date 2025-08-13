#!/usr/bin/env python3
"""Initialize database with schema and seed data."""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prisma import Prisma
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_database():
    """Ensure database exists."""
    logger.info("Checking database connection...")
    
    prisma = Prisma()
    try:
        await prisma.connect()
        logger.info("Database connection successful")
        await prisma.disconnect()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def run_migrations():
    """Run Prisma migrations."""
    logger.info("Running database migrations...")
    
    try:
        # Generate Prisma client
        result = subprocess.run(
            ["prisma", "generate"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent / "infrastructure" / "prisma"
        )
        if result.returncode != 0:
            logger.error(f"Failed to generate Prisma client: {result.stderr}")
            return False
        
        # Run migrations
        result = subprocess.run(
            ["prisma", "migrate", "deploy"],
            capture_output=True,
            text=True,
            env={**os.environ, "DATABASE_URL": "postgresql://tahoe:tahoe@localhost:5432/tahoe"},
            cwd=Path(__file__).parent.parent.parent / "infrastructure" / "prisma"
        )
        if result.returncode != 0:
            logger.error(f"Failed to run migrations: {result.stderr}")
            return False
        
        logger.info("Migrations completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False


async def seed_initial_data(prisma: Prisma):
    """Seed initial configuration data."""
    logger.info("Seeding initial data...")
    
    # Check if already seeded
    existing = await prisma.configurationversion.find_first()
    if existing:
        logger.info("Database already seeded")
        return
    
    # Add default model configuration
    from prisma import Json
    await prisma.configurationversion.create(
        data={
            "type": "model",
            "name": "default",
            "version": "1.0.0",
            "checksum": "default-checksum",
            "specification": Json({
                "provider": "google",
                "model": "gemini-2.0-flash",
                "parameters": {
                    "temperature": 0.2,
                    "max_tokens": 8192
                }
            }),
            "created_by": "system"
        }
    )
    logger.info("Created default model configuration")
    
    # Add development model configuration
    await prisma.configurationversion.create(
        data={
            "type": "model",
            "name": "development",
            "version": "1.0.0",
            "checksum": "dev-checksum",
            "specification": Json({
                "provider": "google",
                "model": "gemini-2.5-flash-lite",
                "parameters": {
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
            }),
            "created_by": "system"
        }
    )
    logger.info("Created development model configuration")
    
    # Add sample tool registration
    await prisma.toolregistry.create(
        data={
            "name": "text_analyzer",
            "version": "1.0.0",
            "description": "Analyzes text for various properties",
            "specification": Json({
                "type": "function",
                "function": {
                    "name": "analyze_text",
                    "description": "Analyzes text content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "analysis_type": {"type": "string"}
                        }
                    }
                }
            }),
            "categories": ["analysis", "text"],
            "dependencies": []
        }
    )
    logger.info("Created sample tool registration")
    
    # Create test session
    test_session = await prisma.session.create(
        data={
            "app_name": "test-app",
            "user_id": "test-user",
            "session_id": "test-session-001",
            "metadata": Json({
                "environment": "development",
                "initialized_by": "seed_script"
            })
        }
    )
    logger.info(f"Created test session: {test_session.session_id}")
    
    # Create test execution
    test_execution = await prisma.execution.create(
        data={
            "session_id": test_session.session_id,
            "agent_name": "test_agent",
            "agent_type": "llm",
            "input_data": Json({"prompt": "Test prompt"}),
            "status": "completed",
            "output_data": Json({"response": "Test response"}),
            "started_at": datetime.now(),
            "completed_at": datetime.now(),
            "duration_ms": 1234
        }
    )
    logger.info(f"Created test execution: {test_execution.id}")
    
    # Create audit log entry
    await prisma.auditlog.create(
        data={
            "user_id": "system",
            "action": "database_seeded",
            "resource": "database",
            "details": Json({
                "timestamp": datetime.now().isoformat(),
                "configurations": 2,
                "tools": 1,
                "sessions": 1
            })
        }
    )
    logger.info("Created audit log entry")
    
    logger.info("Initial data seeded successfully")


async def main():
    """Main initialization function."""
    logger.info("=== Database Initialization ===")
    
    # Check database connection
    if not await create_database():
        logger.error("Failed to connect to database. Ensure PostgreSQL is running.")
        return False
    
    # Run migrations
    if not run_migrations():
        logger.error("Failed to run migrations")
        return False
    
    # Seed data
    prisma = Prisma()
    try:
        await prisma.connect()
        await seed_initial_data(prisma)
        
        # Show statistics
        stats = {
            "sessions": await prisma.session.count(),
            "executions": await prisma.execution.count(),
            "tools": await prisma.toolregistry.count(),
            "configurations": await prisma.configurationversion.count(),
            "audit_logs": await prisma.auditlog.count()
        }
        
        logger.info("=== Database Statistics ===")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        await prisma.disconnect()
        logger.info("=== Database initialized successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        await prisma.disconnect()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)