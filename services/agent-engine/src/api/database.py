"""Database API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from ..services.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/db", tags=["database"])


class SessionRequest(BaseModel):
    """Request model for creating sessions."""

    app_name: str
    user_id: str
    session_id: str
    state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExecutionRequest(BaseModel):
    """Request model for creating executions."""

    session_id: str
    agent_name: str
    agent_type: str
    input_data: Dict[str, Any]
    workflow_name: Optional[str] = None


class ExecutionUpdate(BaseModel):
    """Request model for updating executions."""

    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    token_usage: Optional[Dict[str, Any]] = None


class AuditLogRequest(BaseModel):
    """Request model for audit logs."""

    user_id: str
    action: str
    resource: str
    details: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    execution_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check database health."""
    try:
        db = get_db()
        health = await db.health_check()

        if health["status"] == "healthy":
            return health
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health
            )
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)},
        )


@router.get("/stats")
async def get_statistics() -> Dict[str, Any]:
    """Get database statistics."""
    try:
        db = get_db()
        stats = await db.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {e}",
        )


# Session endpoints
@router.post("/sessions")
async def create_session(request: SessionRequest) -> Dict[str, str]:
    """Create a new session."""
    try:
        db = get_db()
        session_id = await db.create_session(
            app_name=request.app_name,
            user_id=request.user_id,
            session_id=request.session_id,
            state=request.state,
            metadata=request.metadata,
        )
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {e}",
        )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    """Get session by ID."""
    try:
        db = get_db()
        session = await db.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        return session.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {e}",
        )


@router.get("/sessions")
async def list_sessions(
    user_id: Optional[str] = None, app_name: Optional[str] = None, limit: int = 100
) -> List[Dict[str, Any]]:
    """List sessions with optional filters."""
    try:
        db = get_db()
        sessions = await db.list_sessions(
            user_id=user_id, app_name=app_name, limit=limit
        )
        return [session.dict() for session in sessions]
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {e}",
        )


# Execution endpoints
@router.post("/executions")
async def create_execution(request: ExecutionRequest) -> Dict[str, str]:
    """Create a new execution."""
    try:
        db = get_db()
        execution_id = await db.create_execution(
            session_id=request.session_id,
            agent_name=request.agent_name,
            agent_type=request.agent_type,
            input_data=request.input_data,
            workflow_name=request.workflow_name,
        )
        return {"execution_id": execution_id}
    except Exception as e:
        logger.error(f"Failed to create execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create execution: {e}",
        )


@router.put("/executions/{execution_id}")
async def update_execution(
    execution_id: str, update: ExecutionUpdate
) -> Dict[str, str]:
    """Update execution status."""
    try:
        db = get_db()
        success = await db.update_execution(
            execution_id=execution_id,
            status=update.status,
            output_data=update.output_data,
            error_message=update.error_message,
            duration_ms=update.duration_ms,
            token_usage=update.token_usage,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found",
            )

        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update execution: {e}",
        )


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str) -> Dict[str, Any]:
    """Get execution by ID."""
    try:
        db = get_db()
        execution = await db.get_execution(execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution {execution_id} not found",
            )

        return execution.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get execution {execution_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {e}",
        )


# Audit log endpoints
@router.post("/audit-logs")
async def create_audit_log(request: AuditLogRequest) -> Dict[str, str]:
    """Create audit log entry."""
    try:
        db = get_db()
        log_id = await db.create_audit_log(
            user_id=request.user_id,
            action=request.action,
            resource=request.resource,
            details=request.details,
            session_id=request.session_id,
            execution_id=request.execution_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
        )
        return {"log_id": log_id}
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit log: {e}",
        )


@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None, action: Optional[str] = None, limit: int = 100
) -> List[Dict[str, Any]]:
    """Get audit logs with optional filters."""
    try:
        db = get_db()
        logs = await db.get_audit_logs(user_id=user_id, action=action, limit=limit)
        return [log.dict() for log in logs]
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get audit logs: {e}",
        )


# Tool registry endpoints
@router.get("/tools")
async def list_tools(
    active_only: bool = True, category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List tools with optional filters."""
    try:
        db = get_db()
        tools = await db.list_tools(active_only=active_only, category=category)
        return [tool.dict() for tool in tools]
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {e}",
        )


@router.get("/tools/{tool_name}")
async def get_tool(tool_name: str) -> Dict[str, Any]:
    """Get tool by name."""
    try:
        db = get_db()
        tool = await db.get_tool(tool_name)

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool {tool_name} not found",
            )

        return tool.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool {tool_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool: {e}",
        )


# Configuration version endpoints
@router.get("/configurations")
async def list_configuration_versions(
    type: Optional[str] = None, name: Optional[str] = None, active_only: bool = False
) -> List[Dict[str, Any]]:
    """List configuration versions."""
    try:
        db = get_db()
        configs = await db.list_configuration_versions(
            type=type, name=name, active_only=active_only
        )
        return [config.dict() for config in configs]
    except Exception as e:
        logger.error(f"Failed to list configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list configurations: {e}",
        )


@router.get("/configurations/{config_type}/{config_name}")
async def get_configuration_version(
    config_type: str, config_name: str, version: Optional[str] = None
) -> Dict[str, Any]:
    """Get configuration version."""
    try:
        db = get_db()
        config = await db.get_configuration_version(
            type=config_type, name=config_name, version=version
        )

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration {config_type}/{config_name} not found",
            )

        return config.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration {config_type}/{config_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {e}",
        )
