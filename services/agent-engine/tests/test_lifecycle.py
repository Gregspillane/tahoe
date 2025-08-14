"""Test database lifecycle management."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
import logging
from src.services.database import DatabaseService, get_db

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_database_connect_disconnect():
    """Test basic database connection and disconnection."""
    db = DatabaseService()
    
    # Initially not connected
    assert not db._connected
    assert db._connection_count == 0
    
    # Connect
    with patch.object(db.prisma, 'connect', new_callable=AsyncMock) as mock_connect:
        await db.connect()
        mock_connect.assert_called_once()
        assert db._connected
        assert db._connection_count == 1
    
    # Connect again (idempotent)
    with patch.object(db.prisma, 'connect', new_callable=AsyncMock) as mock_connect:
        await db.connect()
        mock_connect.assert_not_called()  # Should not connect again
        assert db._connected
        assert db._connection_count == 1  # Count should not increase
    
    # Disconnect
    with patch.object(db.prisma, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
        await db.disconnect()
        mock_disconnect.assert_called_once()
        assert not db._connected


@pytest.mark.asyncio
async def test_database_ensure_connected():
    """Test ensure_connected method with reconnection."""
    db = DatabaseService()
    
    # Not connected initially
    assert not db._connected
    
    # ensure_connected should connect
    with patch.object(db.prisma, 'connect', new_callable=AsyncMock) as mock_connect:
        with patch.object(db.prisma.session, 'count', new_callable=AsyncMock, return_value=0):
            await db.ensure_connected()
            mock_connect.assert_called_once()
            assert db._connected
    
    # ensure_connected with existing connection (should ping)
    with patch.object(db.prisma.session, 'count', new_callable=AsyncMock, return_value=5) as mock_count:
        await db.ensure_connected()
        mock_count.assert_called_once()  # Should ping to verify connection
        assert db._connected
    
    # ensure_connected with lost connection (should reconnect)
    with patch.object(db.prisma.session, 'count', new_callable=AsyncMock, side_effect=Exception("Connection lost")):
        with patch.object(db.prisma, 'connect', new_callable=AsyncMock) as mock_connect:
            await db.ensure_connected()
            mock_connect.assert_called_once()  # Should reconnect
            assert db._connected


@pytest.mark.asyncio
async def test_connection_context_manager():
    """Test the connection context manager."""
    db = DatabaseService()
    
    with patch.object(db, 'ensure_connected', new_callable=AsyncMock) as mock_ensure:
        async with db.get_connection() as conn:
            mock_ensure.assert_called_once()
            assert conn is db  # Should yield self
        
        # After context, connection should still be alive (not disconnected)
        # This is verified by no disconnect call


@pytest.mark.asyncio
async def test_health_check():
    """Test database health check."""
    db = DatabaseService()
    
    # Mock successful health check
    with patch.object(db, 'connect', new_callable=AsyncMock):
        with patch.object(db.prisma.session, 'count', new_callable=AsyncMock, return_value=10):
            health = await db.health_check()
            assert health['status'] == 'healthy'
            assert health['connected'] == True
            assert health['session_count'] == 10
    
    # Mock failed health check
    with patch.object(db, 'connect', new_callable=AsyncMock, side_effect=Exception("Database error")):
        health = await db.health_check()
        assert health['status'] == 'unhealthy'
        assert health['connected'] == False
        assert 'error' in health


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test that get_db returns singleton instance."""
    db1 = get_db()
    db2 = get_db()
    
    assert db1 is db2  # Should be the same instance


@pytest.mark.asyncio
async def test_disconnect_error_handling():
    """Test error handling during disconnect."""
    db = DatabaseService()
    db._connected = True
    
    # Mock disconnect error
    with patch.object(db.prisma, 'disconnect', new_callable=AsyncMock, side_effect=Exception("Disconnect error")):
        with pytest.raises(Exception) as exc_info:
            await db.disconnect()
        
        # Even on error, should mark as disconnected
        assert not db._connected
        assert "Disconnect error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connect_error_handling():
    """Test error handling during connect."""
    db = DatabaseService()
    
    # Mock connect error
    with patch.object(db.prisma, 'connect', new_callable=AsyncMock, side_effect=Exception("Connection failed")):
        with pytest.raises(Exception) as exc_info:
            await db.connect()
        
        # On error, should remain disconnected
        assert not db._connected
        assert "Connection failed" in str(exc_info.value)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])