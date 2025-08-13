"""Tests for database operations."""

import pytest
import asyncio
import os
from typing import Dict, Any

from src.services.database import DatabaseService, get_db
from prisma import Json


@pytest.fixture
async def db_service():
    """Database service fixture."""
    # Set environment variable for testing
    os.environ["DATABASE_URL"] = "postgresql://tahoe:tahoe@localhost:5432/tahoe"
    
    service = DatabaseService()
    await service.connect()
    yield service
    await service.disconnect()


@pytest.mark.asyncio
async def test_database_health_check(db_service):
    """Test database health check."""
    health = await db_service.health_check()
    
    assert health["status"] == "healthy"
    assert health["connected"] is True
    assert "session_count" in health


@pytest.mark.asyncio
async def test_session_operations(db_service):
    """Test session CRUD operations."""
    # Create session
    session_id = await db_service.create_session(
        app_name="test-app",
        user_id="test-user",
        session_id="test-session-123",
        state={"test": "state"},
        metadata={"test": "metadata"}
    )
    
    assert session_id is not None
    
    # Get session
    session = await db_service.get_session("test-session-123")
    assert session is not None
    assert session.app_name == "test-app"
    assert session.user_id == "test-user"
    assert session.state == {"test": "state"}
    
    # Update session state
    success = await db_service.update_session_state(
        "test-session-123",
        {"updated": "state"}
    )
    assert success is True
    
    # List sessions
    sessions = await db_service.list_sessions(user_id="test-user")
    assert len(sessions) >= 1
    
    # Verify updated state
    updated_session = await db_service.get_session("test-session-123")
    assert updated_session.state == {"updated": "state"}


@pytest.mark.asyncio
async def test_execution_operations(db_service):
    """Test execution tracking."""
    # First create a session
    session_id = await db_service.create_session(
        app_name="test-app",
        user_id="test-user",
        session_id="test-session-exec"
    )
    
    # Create execution
    execution_id = await db_service.create_execution(
        session_id="test-session-exec",
        agent_name="test_agent",
        agent_type="llm",
        input_data={"prompt": "Test prompt"},
        workflow_name="test_workflow"
    )
    
    assert execution_id is not None
    
    # Update execution
    success = await db_service.update_execution(
        execution_id=execution_id,
        status="completed",
        output_data={"response": "Test response"},
        duration_ms=1500,
        token_usage={"input": 10, "output": 20}
    )
    assert success is True
    
    # Get execution
    execution = await db_service.get_execution(execution_id)
    assert execution is not None
    assert execution.status == "completed"
    assert execution.output_data == {"response": "Test response"}
    assert execution.duration_ms == 1500


@pytest.mark.asyncio
async def test_result_storage(db_service):
    """Test result storage."""
    # Create session and execution first
    session_id = await db_service.create_session(
        app_name="test-app",
        user_id="test-user",
        session_id="test-session-result"
    )
    
    execution_id = await db_service.create_execution(
        session_id="test-session-result",
        agent_name="test_agent",
        agent_type="llm",
        input_data={"prompt": "Test"}
    )
    
    # Create result
    result_id = await db_service.create_result(
        execution_id=execution_id,
        result_type="final",
        data={"result": "test result"},
        metadata={"confidence": 0.95}
    )
    
    assert result_id is not None


@pytest.mark.asyncio
async def test_audit_logging(db_service):
    """Test audit logging."""
    # Create audit log
    log_id = await db_service.create_audit_log(
        user_id="test-user",
        action="test_action",
        resource="test_resource",
        details={"test": "details"},
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    
    assert log_id is not None
    
    # Get audit logs
    logs = await db_service.get_audit_logs(user_id="test-user")
    assert len(logs) >= 1
    
    # Check log content
    user_logs = [log for log in logs if log.action == "test_action"]
    assert len(user_logs) >= 1
    assert user_logs[0].resource == "test_resource"


@pytest.mark.asyncio
async def test_tool_registry(db_service):
    """Test tool registry operations."""
    # Register tool
    tool_id = await db_service.register_tool(
        name="test_tool",
        version="1.0.0",
        specification={
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "Test function"
            }
        },
        description="Test tool for testing",
        categories=["test", "utility"],
        dependencies=["pytest"]
    )
    
    assert tool_id is not None
    
    # Get tool
    tool = await db_service.get_tool("test_tool")
    assert tool is not None
    assert tool.name == "test_tool"
    assert tool.version == "1.0.0"
    assert "test" in tool.categories
    
    # List tools
    tools = await db_service.list_tools(category="test")
    test_tools = [t for t in tools if t.name == "test_tool"]
    assert len(test_tools) >= 1


@pytest.mark.asyncio
async def test_configuration_versioning(db_service):
    """Test configuration versioning."""
    # Save configuration
    config_id = await db_service.save_configuration_version(
        type="agent",
        name="test_agent",
        version="1.0.0",
        checksum="test-checksum",
        specification={
            "type": "llm",
            "model": "gemini-2.0-flash",
            "instruction": "Test agent"
        },
        created_by="test-user"
    )
    
    assert config_id is not None
    
    # Get configuration (active version)
    config = await db_service.get_configuration_version(
        type="agent",
        name="test_agent"
    )
    assert config is not None
    assert config.version == "1.0.0"
    assert config.active is True
    
    # Get specific version
    config_v1 = await db_service.get_configuration_version(
        type="agent",
        name="test_agent",
        version="1.0.0"
    )
    assert config_v1 is not None
    assert config_v1.version == "1.0.0"
    
    # List configurations
    configs = await db_service.list_configuration_versions(
        type="agent",
        active_only=True
    )
    test_configs = [c for c in configs if c.name == "test_agent"]
    assert len(test_configs) >= 1


@pytest.mark.asyncio
async def test_statistics(db_service):
    """Test database statistics."""
    stats = await db_service.get_statistics()
    
    assert "sessions" in stats
    assert "executions" in stats
    assert "results" in stats
    assert "audit_logs" in stats
    assert "tools" in stats
    assert "configurations" in stats
    assert "execution_status" in stats
    
    # Check execution status breakdown
    status_stats = stats["execution_status"]
    assert "pending" in status_stats
    assert "running" in status_stats
    assert "completed" in status_stats
    assert "failed" in status_stats


@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test database service singleton."""
    db1 = get_db()
    db2 = get_db()
    
    assert db1 is db2  # Same instance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])