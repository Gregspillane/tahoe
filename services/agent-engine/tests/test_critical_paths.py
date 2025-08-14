"""Basic integration tests for critical paths - KISS approach."""

import pytest
import asyncio
import json
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prisma import Prisma
from src.services.database import DatabaseService


@pytest.fixture
async def db_service():
    """Database service fixture."""
    service = DatabaseService()
    await service.connect()
    try:
        yield service
    finally:
        await service.disconnect()


@pytest.fixture
async def clean_test_data(db_service):
    """Clean up test data before and after tests."""
    # Clean before test
    prisma = db_service.prisma
    await prisma.session.delete_many(where={"app_name": {"startswith": "test_"}})
    await prisma.configurationversion.delete_many(where={"type": "test"})
    await prisma.configurationversion.delete_many(where={"type": "agent", "name": "test_agent"})
    
    yield
    
    # Clean after test
    await prisma.session.delete_many(where={"app_name": {"startswith": "test_"}})
    await prisma.configurationversion.delete_many(where={"type": "test"})
    await prisma.configurationversion.delete_many(where={"type": "agent", "name": "test_agent"})


@pytest.mark.asyncio
async def test_basic_session_lifecycle(db_service, clean_test_data):
    """Test basic session creation and retrieval - happy path."""
    # Create session
    session_id = await db_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session_123",
        state={"key": "value"},
        metadata={"test": True}
    )
    
    assert session_id is not None
    
    # Retrieve session
    session = await db_service.get_session("test_session_123")
    assert session is not None
    assert session.app_name == "test_app"
    assert session.user_id == "test_user"
    # State is JSON-encoded
    import json
    state = json.loads(session.state)
    assert state["key"] == "value"


@pytest.mark.asyncio
async def test_execution_tracking(db_service, clean_test_data):
    """Test execution creation and update - critical for tracking."""
    # Create session first
    session_id = await db_service.create_session(
        app_name="test_exec_app",
        user_id="test_user",
        session_id="test_exec_session"
    )
    
    # Create execution
    exec_id = await db_service.create_execution(
        session_id=session_id,
        agent_name="test_agent",
        agent_type="LlmAgent",
        input_data={"query": "test"}
    )
    
    assert exec_id is not None
    
    # Update execution
    success = await db_service.update_execution(
        execution_id=exec_id,
        status="completed",
        output_data={"result": "success"},
        duration_ms=100
    )
    
    assert success is True
    
    # Verify update
    execution = await db_service.get_execution(exec_id)
    assert execution.status == "completed"
    # Output data is JSON-encoded
    import json
    output = json.loads(execution.output_data)
    assert output["result"] == "success"


@pytest.mark.asyncio
async def test_cascade_delete(db_service, clean_test_data):
    """Test cascade delete works - prevents orphaned data."""
    # Create hierarchy: Session -> Execution -> Result
    session_id = await db_service.create_session(
        app_name="test_cascade",
        user_id="test_user",
        session_id="test_cascade_session"
    )
    
    exec_id = await db_service.create_execution(
        session_id=session_id,
        agent_name="test_agent",
        agent_type="LlmAgent",
        input_data={"test": True}
    )
    
    result_id = await db_service.create_result(
        execution_id=exec_id,
        result_type="test",
        data={"result": "test_data"}
    )
    
    # Delete session - should cascade
    deleted = await db_service.prisma.session.delete(
        where={"id": session_id}
    )
    
    assert deleted is not None
    
    # Verify cascade worked
    execution = await db_service.get_execution(exec_id)
    assert execution is None  # Should be deleted
    
    result = await db_service.prisma.result.find_unique(where={"id": result_id})
    assert result is None  # Should be deleted


@pytest.mark.asyncio
async def test_transaction_rollback(db_service, clean_test_data):
    """Test transaction wrapper rollback on error."""
    
    async def failing_operation(tx):
        # First operation succeeds
        await tx.configurationversion.update_many(
            where={"type": "test", "name": "config", "active": True},
            data={"active": False}
        )
        
        # Second operation fails with invalid data
        # Intentionally cause error by missing required field
        await tx.configurationversion.create(
            data={
                "type": "test",
                "name": "config",
                # Missing required fields: version, checksum, specification
            }
        )
    
    # Should raise error and rollback
    with pytest.raises(Exception):
        await db_service.transaction(failing_operation)
    
    # Verify no partial changes were made
    configs = await db_service.prisma.configurationversion.find_many(
        where={"type": "test", "name": "config"}
    )
    # Should be empty or all should still be active if they existed
    for config in configs:
        assert config.active == True


@pytest.mark.asyncio
async def test_configuration_versioning_atomic(db_service, clean_test_data):
    """Test configuration versioning is atomic - no partial updates."""
    # Create initial version
    v1_id = await db_service.save_configuration_version(
        type="agent",
        name="test_agent",
        version="1.0.0",
        checksum="abc123",
        specification={"version": 1}
    )
    
    # Create v2 - should deactivate v1 atomically
    v2_id = await db_service.save_configuration_version(
        type="agent",
        name="test_agent",
        version="2.0.0",
        checksum="def456",
        specification={"version": 2}
    )
    
    # Check only v2 is active
    v1 = await db_service.prisma.configurationversion.find_unique(where={"id": v1_id})
    v2 = await db_service.prisma.configurationversion.find_unique(where={"id": v2_id})
    
    assert v1.active == False
    assert v2.active == True
    
    # Verify only one active version
    active_configs = await db_service.prisma.configurationversion.find_many(
        where={"type": "agent", "name": "test_agent", "active": True}
    )
    assert len(active_configs) == 1
    assert active_configs[0].version == "2.0.0"


if __name__ == "__main__":
    # Quick smoke test - run with: python tests/test_critical_paths.py
    async def run_smoke_test():
        print("Running smoke tests...")
        service = DatabaseService()
        
        try:
            await service.connect()
            print("✅ Database connected")
            
            # Test basic operation
            session_id = await service.create_session(
                app_name=f"smoke_test_{datetime.now().isoformat()}",
                user_id="smoke_user",
                session_id=f"smoke_{datetime.now().isoformat()}"
            )
            print(f"✅ Created session: {session_id}")
            
            # Test transaction
            async def test_tx(tx):
                count = await tx.session.count()
                return count
            
            count = await service.transaction(test_tx)
            print(f"✅ Transaction worked, session count: {count}")
            
            # Cleanup
            await service.prisma.session.delete(where={"id": session_id})
            print("✅ Cleanup completed")
            
        finally:
            await service.disconnect()
            print("✅ Database disconnected")
        
        print("\n✨ All smoke tests passed!")
    
    asyncio.run(run_smoke_test())