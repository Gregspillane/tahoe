#!/usr/bin/env python
"""Manual test script for database lifecycle management."""

import asyncio
import signal
import sys
import logging
from src.services.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_lifecycle():
    """Test database lifecycle management."""
    logger.info("Starting lifecycle test...")
    
    # Get database service
    db = get_db()
    
    # Test initial state
    logger.info(f"Initial state - Connected: {db._connected}")
    
    # Test connect
    logger.info("Testing connect...")
    await db.connect()
    logger.info(f"After connect - Connected: {db._connected}, Count: {db._connection_count}")
    
    # Test idempotent connect
    logger.info("Testing idempotent connect...")
    await db.connect()
    logger.info(f"After second connect - Connected: {db._connected}, Count: {db._connection_count}")
    
    # Test health check
    logger.info("Testing health check...")
    health = await db.health_check()
    logger.info(f"Health check result: {health}")
    
    # Test statistics
    logger.info("Testing statistics...")
    stats = await db.get_statistics()
    logger.info(f"Statistics: {stats}")
    
    # Test ensure_connected
    logger.info("Testing ensure_connected...")
    await db.ensure_connected()
    logger.info(f"After ensure_connected - Connected: {db._connected}")
    
    # Test disconnect
    logger.info("Testing disconnect...")
    await db.disconnect()
    logger.info(f"After disconnect - Connected: {db._connected}")
    
    # Test reconnect
    logger.info("Testing reconnect...")
    await db.connect()
    logger.info(f"After reconnect - Connected: {db._connected}, Count: {db._connection_count}")
    
    # Final disconnect
    logger.info("Final disconnect...")
    await db.disconnect()
    logger.info(f"Final state - Connected: {db._connected}")
    
    logger.info("Lifecycle test complete!")


async def test_with_signal():
    """Test with signal handling to simulate shutdown."""
    logger.info("Starting signal test...")
    
    db = get_db()
    
    # Connect
    await db.connect()
    logger.info("Database connected, press Ctrl+C to test shutdown...")
    
    # Set up signal handler
    def signal_handler(signum, frame):
        logger.info("Signal received, initiating shutdown...")
        asyncio.create_task(shutdown())
    
    async def shutdown():
        logger.info("Shutting down...")
        await db.disconnect()
        logger.info("Shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
            # Periodically check connection
            await db.ensure_connected()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--signal":
        asyncio.run(test_with_signal())
    else:
        asyncio.run(test_lifecycle())