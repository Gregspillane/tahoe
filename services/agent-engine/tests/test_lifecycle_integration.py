"""Integration test for database lifecycle management.

This tests the actual lifecycle behavior without mocking Prisma internals,
since Prisma's methods are read-only by design.
"""

import asyncio
import pytest
import logging
from src.services.database import DatabaseService, get_db
from unittest.mock import Mock, patch

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_database_lifecycle_integration():
    """Test the actual database lifecycle without mocking Prisma internals.
    
    This is an integration test that verifies our lifecycle management
    works correctly with the real Prisma client behavior.
    """
    # Create a new instance for testing
    db = DatabaseService()
    
    # Initial state
    assert not db._connected
    assert db._connection_count == 0
    
    try:
        # Test connect
        await db.connect()
        assert db._connected
        assert db._connection_count == 1
        logger.info(f"Connected successfully, connection count: {db._connection_count}")
        
        # Test idempotent connect
        await db.connect()
        assert db._connected
        assert db._connection_count == 1  # Should not increase
        logger.info("Idempotent connect works correctly")
        
        # Test health check
        health = await db.health_check()
        assert health['status'] in ['healthy', 'unhealthy']
        assert 'connected' in health
        logger.info(f"Health check result: {health}")
        
        # Test ensure_connected when already connected
        await db.ensure_connected()
        assert db._connected
        logger.info("ensure_connected maintains existing connection")
        
    finally:
        # Always disconnect in cleanup
        if db._connected:
            await db.disconnect()
            assert not db._connected
            logger.info("Disconnected successfully")


@pytest.mark.asyncio
async def test_database_reconnection():
    """Test reconnection behavior after disconnect."""
    db = DatabaseService()
    
    try:
        # Connect
        await db.connect()
        initial_count = db._connection_count
        assert db._connected
        
        # Disconnect
        await db.disconnect()
        assert not db._connected
        
        # Reconnect
        await db.connect()
        assert db._connected
        assert db._connection_count == initial_count + 1  # Count should increase
        logger.info(f"Reconnection successful, new count: {db._connection_count}")
        
    finally:
        if db._connected:
            await db.disconnect()


@pytest.mark.asyncio
async def test_context_manager():
    """Test the connection context manager."""
    db = DatabaseService()
    
    try:
        initial_connected = db._connected
        
        async with db.get_connection() as conn:
            # Should be connected within context
            assert conn is db
            assert db._connected
            logger.info("Context manager ensures connection")
        
        # Should still be connected after context (no auto-disconnect)
        assert db._connected
        logger.info("Context manager preserves connection for reuse")
        
    finally:
        if db._connected:
            await db.disconnect()


@pytest.mark.asyncio 
async def test_singleton_behavior():
    """Test singleton pattern for get_db."""
    db1 = get_db()
    db2 = get_db()
    
    assert db1 is db2
    logger.info("Singleton pattern working correctly")


class TestDatabaseServiceUnit:
    """Unit tests that don't require actual database connection.
    
    These tests mock at a higher level or test logic that doesn't
    directly interact with Prisma's read-only methods.
    """
    
    def test_initialization(self):
        """Test DatabaseService initialization."""
        with patch.dict('os.environ', {
            'ADK_SESSION_SERVICE': 'test_backend',
            'AGENT_ENGINE_REDIS_NAMESPACE': 'test:'
        }):
            db = DatabaseService()
            assert db.session_backend == 'test_backend'
            assert db.redis_namespace == 'test:'
            assert not db._connected
            assert db._connection_count == 0
    
    @pytest.mark.asyncio
    async def test_connection_tracking(self):
        """Test connection counting logic."""
        db = DatabaseService()
        
        # Mock the Prisma instance itself, not its methods
        mock_prisma = Mock()
        mock_prisma.connect = Mock(return_value=asyncio.Future())
        mock_prisma.connect.return_value.set_result(None)
        mock_prisma.disconnect = Mock(return_value=asyncio.Future())
        mock_prisma.disconnect.return_value.set_result(None)
        
        # Replace the entire prisma instance
        with patch.object(db, 'prisma', mock_prisma):
            # Now we can test our logic
            await db.connect()
            assert db._connected
            assert db._connection_count == 1
            
            await db.connect()  # Idempotent
            assert db._connection_count == 1
            
            await db.disconnect()
            assert not db._connected


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])