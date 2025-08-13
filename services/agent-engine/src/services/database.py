"""Database service layer using Prisma ORM."""

from prisma import Prisma
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import logging
import os
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations using Prisma."""
    
    def __init__(self):
        """Initialize database service."""
        self.prisma = Prisma()
        self._connected = False
        # Get backend from environment
        self.session_backend = os.getenv("ADK_SESSION_SERVICE", "memory")
        # Redis namespace for service isolation
        self.redis_namespace = os.getenv("AGENT_ENGINE_REDIS_NAMESPACE", "agent:")
    
    async def connect(self) -> None:
        """Connect to database."""
        if not self._connected:
            await self.prisma.connect()
            self._connected = True
            logger.info("Database connected")
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self._connected:
            await self.prisma.disconnect()
            self._connected = False
            logger.info("Database disconnected")
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connection."""
        try:
            await self.connect()
            yield self
        finally:
            pass  # Keep connection alive for reuse
    
    # Session operations with ADK compatibility
    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        backend: Optional[str] = None
    ) -> str:
        """Create new session record with proper ADK fields."""
        await self.connect()
        
        session = await self.prisma.session.create(
            data={
                "app_name": app_name,  # Separate field
                "user_id": user_id,    # Separate field
                "session_id": session_id,  # Actual session ID
                "state": state,
                "backend": backend or self.session_backend,  # Track backend
                "metadata": metadata or {"source": "adk", "namespace": self.redis_namespace}
            }
        )
        logger.info(f"Created session: {session.id}")
        return session.id
    
    async def get_session(self, session_id: str) -> Optional[Any]:
        """Get session by ID."""
        await self.connect()
        
        session = await self.prisma.session.find_unique(
            where={"session_id": session_id},
            include={"executions": True}
        )
        return session
    
    async def update_session_state(
        self,
        session_id: str,
        state_delta: Dict[str, Any]
    ) -> bool:
        """Update session state with delta."""
        await self.connect()
        
        # Get current session state
        session = await self.get_session(session_id)
        if session:
            current_state = session.state or {}
            current_state.update(state_delta)
            
            updated_session = await self.prisma.session.update(
                where={"session_id": session_id},
                data={"state": current_state}
            )
            return updated_session is not None
        return False
    
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        app_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Any]:
        """List sessions with optional filters."""
        await self.connect()
        
        where = {}
        if user_id:
            where["user_id"] = user_id
        if app_name:
            where["app_name"] = app_name
        
        sessions = await self.prisma.session.find_many(
            where=where,
            take=limit,
            order={"created_at": "desc"}
        )
        return sessions
    
    # Execution tracking
    async def create_execution(
        self,
        session_id: str,
        agent_name: str,
        agent_type: str,
        input_data: Dict[str, Any],
        workflow_name: Optional[str] = None
    ) -> str:
        """Create execution record."""
        await self.connect()
        
        execution = await self.prisma.execution.create(
            data={
                "session_id": session_id,
                "agent_name": agent_name,
                "agent_type": agent_type,
                "workflow_name": workflow_name,
                "input_data": input_data,
                "status": "pending"
            }
        )
        logger.info(f"Created execution: {execution.id}")
        return execution.id
    
    async def update_execution(
        self,
        execution_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        token_usage: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update execution status."""
        await self.connect()
        
        data = {"status": status}
        
        if status in ["completed", "failed"]:
            data["completed_at"] = datetime.now()
        
        if output_data is not None:
            data["output_data"] = output_data
        
        if error_message:
            data["error_message"] = error_message
        
        if duration_ms is not None:
            data["duration_ms"] = duration_ms
        
        if token_usage:
            data["token_usage"] = token_usage
        
        execution = await self.prisma.execution.update(
            where={"id": execution_id},
            data=data
        )
        
        logger.info(f"Updated execution {execution_id}: status={status}")
        return execution is not None
    
    async def get_execution(self, execution_id: str) -> Optional[Any]:
        """Get execution by ID."""
        await self.connect()
        
        execution = await self.prisma.execution.find_unique(
            where={"id": execution_id},
            include={"results": True}
        )
        return execution
    
    # Result storage
    async def create_result(
        self,
        execution_id: str,
        result_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create result record."""
        await self.connect()
        
        result = await self.prisma.result.create(
            data={
                "execution_id": execution_id,
                "result_type": result_type,
                "data": data,
                "metadata": metadata
            }
        )
        logger.info(f"Created result: {result.id}")
        return result.id
    
    # Audit logging
    async def create_audit_log(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Create audit log entry."""
        await self.connect()
        
        audit_log = await self.prisma.auditlog.create(
            data={
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "details": details,
                "session_id": session_id,
                "execution_id": execution_id,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
        )
        logger.debug(f"Audit log: {action} on {resource} by {user_id}")
        return audit_log.id
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Any]:
        """Get audit logs with optional filters."""
        await self.connect()
        
        where = {}
        if user_id:
            where["user_id"] = user_id
        if action:
            where["action"] = action
        
        logs = await self.prisma.auditlog.find_many(
            where=where,
            take=limit,
            order={"created_at": "desc"}
        )
        return logs
    
    # Tool registry
    async def register_tool(
        self,
        name: str,
        version: str,
        specification: Dict[str, Any],
        description: Optional[str] = None,
        function_def: Optional[str] = None,
        categories: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Register a new tool."""
        await self.connect()
        
        tool = await self.prisma.toolregistry.create(
            data={
                "name": name,
                "version": version,
                "description": description,
                "specification": specification,
                "function_def": function_def,
                "categories": categories or [],
                "dependencies": dependencies or []
            }
        )
        logger.info(f"Registered tool: {name} v{version}")
        return tool.id
    
    async def get_tool(self, name: str) -> Optional[Any]:
        """Get tool by name."""
        await self.connect()
        
        tool = await self.prisma.toolregistry.find_unique(
            where={"name": name}
        )
        return tool
    
    async def list_tools(
        self,
        active_only: bool = True,
        category: Optional[str] = None
    ) -> List[Any]:
        """List tools with optional filters."""
        await self.connect()
        
        where = {}
        if active_only:
            where["active"] = True
        if category:
            where["categories"] = {"has": category}
        
        tools = await self.prisma.toolregistry.find_many(
            where=where,
            order={"name": "asc"}
        )
        return tools
    
    # Configuration versioning
    async def save_configuration_version(
        self,
        type: str,
        name: str,
        version: str,
        checksum: str,
        specification: Dict[str, Any],
        created_by: str = "system"
    ) -> str:
        """Save configuration version."""
        await self.connect()
        
        # Deactivate previous versions
        await self.prisma.configurationversion.update_many(
            where={
                "type": type,
                "name": name,
                "active": True
            },
            data={"active": False}
        )
        
        config = await self.prisma.configurationversion.create(
            data={
                "type": type,
                "name": name,
                "version": version,
                "checksum": checksum,
                "specification": specification,
                "created_by": created_by,
                "active": True
            }
        )
        logger.info(f"Saved configuration: {type}/{name} v{version}")
        return config.id
    
    async def get_configuration_version(
        self,
        type: str,
        name: str,
        version: Optional[str] = None
    ) -> Optional[Any]:
        """Get configuration version."""
        await self.connect()
        
        if version:
            config = await self.prisma.configurationversion.find_first(
                where={
                    "type": type,
                    "name": name,
                    "version": version
                }
            )
        else:
            # Get active version
            config = await self.prisma.configurationversion.find_first(
                where={
                    "type": type,
                    "name": name,
                    "active": True
                }
            )
        
        return config
    
    async def list_configuration_versions(
        self,
        type: Optional[str] = None,
        name: Optional[str] = None,
        active_only: bool = False
    ) -> List[Any]:
        """List configuration versions."""
        await self.connect()
        
        where = {}
        if type:
            where["type"] = type
        if name:
            where["name"] = name
        if active_only:
            where["active"] = True
        
        configs = await self.prisma.configurationversion.find_many(
            where=where,
            order={"created_at": "desc"}
        )
        return configs
    
    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        try:
            await self.connect()
            # Simple query to verify connection
            count = await self.prisma.session.count()
            return {
                "status": "healthy",
                "connected": True,
                "backend": self.session_backend,
                "session_count": count
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "backend": self.session_backend,
                "error": str(e)
            }
    
    # Statistics
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        await self.connect()
        
        stats = {
            "sessions": await self.prisma.session.count(),
            "executions": await self.prisma.execution.count(),
            "results": await self.prisma.result.count(),
            "audit_logs": await self.prisma.auditlog.count(),
            "tools": await self.prisma.toolregistry.count(),
            "configurations": await self.prisma.configurationversion.count()
        }
        
        # Get execution status breakdown
        pending = await self.prisma.execution.count(where={"status": "pending"})
        running = await self.prisma.execution.count(where={"status": "running"})
        completed = await self.prisma.execution.count(where={"status": "completed"})
        failed = await self.prisma.execution.count(where={"status": "failed"})
        
        stats["execution_status"] = {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed
        }
        
        return stats


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_db() -> DatabaseService:
    """Get database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


async def init_database() -> None:
    """Initialize database connection."""
    db = get_db()
    await db.connect()
    logger.info("Database initialized")