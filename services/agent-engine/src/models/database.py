"""
Database models and utilities for agent-engine service
"""

from prisma import Prisma
from typing import Optional, Dict, Any
import json
import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Simple retry decorator for database operations
async def retry_db_operation(func, max_retries=3, base_delay=1):
    """
    Simple retry mechanism for database operations.
    Only retries on connection errors, not business logic errors.
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            # Only retry on connection-related errors
            error_msg = str(e).lower()
            if any(x in error_msg for x in ['connection', 'timeout', 'closed', 'terminated']):
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                    raise
            else:
                # Don't retry on non-connection errors
                raise

# Global database instance
db = Prisma()

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.db = db
        self._connected = False
    
    async def connect(self):
        """Connect to the database"""
        if not self._connected:
            await self.db.connect()
            self._connected = True
            print("✅ Connected to PostgreSQL database")
    
    async def disconnect(self):
        """Disconnect from the database"""
        if self._connected:
            await self.db.disconnect()
            self._connected = False
            print("📴 Disconnected from PostgreSQL database")
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions"""
        async with self.db.tx() as transaction:
            yield transaction
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            # Simple query to verify connection
            await self.db.agenttemplate.count()
            return True
        except Exception:
            return False

# Singleton instance
database_manager = DatabaseManager()

# Utility functions for working with JSON fields
def serialize_json(data: Any) -> str:
    """Serialize data to JSON string for storage"""
    if data is None:
        return None
    return json.dumps(data) if not isinstance(data, str) else data

def deserialize_json(data: str) -> Any:
    """Deserialize JSON string from storage"""
    if data is None:
        return None
    return json.loads(data) if isinstance(data, str) else data

# Model helpers
class AgentTemplateHelper:
    """Helper functions for AgentTemplate model"""
    
    @staticmethod
    async def get_active_agents():
        """Get all active agent templates"""
        return await db.agenttemplate.find_many(
            where={"isActive": True},
            order={"name": "asc"}
        )
    
    @staticmethod
    async def get_by_capability(capability: str):
        """Find agents with a specific capability"""
        return await db.agenttemplate.find_many(
            where={
                "AND": [
                    {"isActive": True},
                    {"capabilities": {"has": capability}}
                ]
            }
        )

class ScorecardHelper:
    """Helper functions for Scorecard model"""
    
    @staticmethod
    async def get_with_agents(scorecard_id: str):
        """Get scorecard with all associated agents"""
        return await db.scorecard.find_unique(
            where={"id": scorecard_id},
            include={
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            }
        )
    
    @staticmethod
    async def get_portfolio_scorecards(portfolio_id: str):
        """Get all active scorecards for a portfolio"""
        return await db.scorecard.find_many(
            where={
                "AND": [
                    {"portfolioId": portfolio_id},
                    {"isActive": True}
                ]
            },
            order={"name": "asc"}
        )

class AnalysisHelper:
    """Helper functions for Analysis model"""
    
    @staticmethod
    async def create_analysis(
        interaction_id: str,
        portfolio_id: str,
        scorecard_id: str,
        trace_id: Optional[str] = None
    ):
        """Create a new analysis record"""
        return await db.analysis.create(
            data={
                "interactionId": interaction_id,
                "portfolioId": portfolio_id,
                "scorecardId": scorecard_id,
                "status": "pending",
                "traceId": trace_id,
                "metadata": serialize_json({})
            }
        )
    
    @staticmethod
    async def update_status(
        analysis_id: str,
        status: str,
        **kwargs
    ):
        """Update analysis status and optional fields"""
        update_data = {"status": status}
        
        # Add optional fields if provided
        for key, value in kwargs.items():
            if key in ["results", "agentOutputs", "metadata"]:
                update_data[key] = serialize_json(value)
            else:
                update_data[key] = value
        
        return await db.analysis.update(
            where={"id": analysis_id},
            data=update_data
        )
    
    @staticmethod
    async def get_recent_analyses(
        portfolio_id: str,
        limit: int = 10
    ):
        """Get recent analyses for a portfolio"""
        return await db.analysis.find_many(
            where={"portfolioId": portfolio_id},
            order={"createdAt": "desc"},
            take=limit
        )

# Export database instance and helpers
__all__ = [
    'db',
    'database_manager',
    'DatabaseManager',
    'AgentTemplateHelper',
    'ScorecardHelper',
    'AnalysisHelper',
    'serialize_json',
    'deserialize_json'
]