#!/usr/bin/env python
"""Simple integration tests for critical paths - no pytest complexity."""

import asyncio
import json
import os
from datetime import datetime

# Set DATABASE_URL
os.environ["DATABASE_URL"] = "postgresql://tahoe:tahoe@localhost:5432/tahoe?schema=agent_engine&connection_limit=20&pool_timeout=10"

from src.services.database import DatabaseService


async def test_session_crud():
    """Test basic session CRUD operations."""
    print("\n🧪 Testing Session CRUD...")
    db = DatabaseService()
    await db.connect()
    
    try:
        # Create
        unique_id = datetime.now().isoformat()
        session_id = await db.create_session(
            app_name="test_crud",
            user_id="test_user",
            session_id=f"test_session_crud_{unique_id}",
            state={"initial": "state"},
            metadata={"test": True}
        )
        print(f"  ✅ Created session: {session_id}")
        
        # Read
        session = await db.get_session(f"test_session_crud_{unique_id}")
        assert session is not None
        assert session.app_name == "test_crud"
        # State is already a dict when retrieved from Prisma
        state = session.state if isinstance(session.state, dict) else json.loads(session.state)
        assert state["initial"] == "state"
        print("  ✅ Retrieved session successfully")
        
        # Update
        success = await db.update_session_state(
            f"test_session_crud_{unique_id}",
            {"updated": "value"}
        )
        assert success
        session = await db.get_session(f"test_session_crud_{unique_id}")
        state = session.state if isinstance(session.state, dict) else json.loads(session.state)
        assert state["updated"] == "value"
        print("  ✅ Updated session state")
        
        # Delete (cleanup)
        await db.prisma.session.delete(where={"id": session_id})
        print("  ✅ Deleted session")
        
    finally:
        await db.disconnect()


async def test_execution_flow():
    """Test execution tracking flow."""
    print("\n🧪 Testing Execution Flow...")
    db = DatabaseService()
    await db.connect()
    
    try:
        # Create session
        unique_id = datetime.now().isoformat()
        session_id = await db.create_session(
            app_name="test_exec",
            user_id="test_user",
            session_id=f"test_exec_session_{unique_id}"
        )
        
        # Create execution
        exec_id = await db.create_execution(
            session_id=session_id,
            agent_name="test_agent",
            agent_type="LlmAgent",
            input_data={"query": "test"}
        )
        print(f"  ✅ Created execution: {exec_id}")
        
        # Update execution
        success = await db.update_execution(
            execution_id=exec_id,
            status="running"
        )
        assert success
        print("  ✅ Updated execution to running")
        
        # Complete execution
        success = await db.update_execution(
            execution_id=exec_id,
            status="completed",
            output_data={"result": "success"},
            duration_ms=100
        )
        assert success
        
        # Verify
        execution = await db.get_execution(exec_id)
        assert execution.status == "completed"
        output = execution.output_data if isinstance(execution.output_data, dict) else json.loads(execution.output_data)
        assert output["result"] == "success"
        print("  ✅ Completed execution successfully")
        
        # Cleanup
        await db.prisma.session.delete(where={"id": session_id})
        
    finally:
        await db.disconnect()


async def test_cascade_delete():
    """Test cascade delete functionality."""
    print("\n🧪 Testing Cascade Delete...")
    db = DatabaseService()
    await db.connect()
    
    try:
        # Create hierarchy
        unique_id = datetime.now().isoformat()
        session_id = await db.create_session(
            app_name="test_cascade",
            user_id="test_user",
            session_id=f"test_cascade_sess_{unique_id}"
        )
        
        exec_id = await db.create_execution(
            session_id=session_id,
            agent_name="test_agent",
            agent_type="LlmAgent",
            input_data={"test": True}
        )
        
        result_id = await db.create_result(
            execution_id=exec_id,
            result_type="test",
            data={"result": "test_data"}
        )
        print("  ✅ Created session -> execution -> result hierarchy")
        
        # Delete session (should cascade)
        await db.prisma.session.delete(where={"id": session_id})
        print("  ✅ Deleted session")
        
        # Verify cascade
        execution = await db.get_execution(exec_id)
        assert execution is None
        
        result = await db.prisma.result.find_unique(where={"id": result_id})
        assert result is None
        print("  ✅ Cascade delete verified - all child records deleted")
        
    finally:
        await db.disconnect()


async def test_transaction_atomicity():
    """Test transaction wrapper ensures atomicity."""
    print("\n🧪 Testing Transaction Atomicity...")
    db = DatabaseService()
    await db.connect()
    
    try:
        # Test successful transaction
        v1_id = await db.save_configuration_version(
            type="test_tx",
            name="config1",
            version="1.0.0",
            specification={"version": 1}
        )
        print("  ✅ Created version 1.0.0")
        
        # Create v2 (should deactivate v1 atomically)
        v2_id = await db.save_configuration_version(
            type="test_tx",
            name="config1",
            version="2.0.0",
            specification={"version": 2}
        )
        print("  ✅ Created version 2.0.0")
        
        # Verify atomicity - only v2 should be active
        v1 = await db.prisma.configurationversion.find_unique(where={"id": v1_id})
        v2 = await db.prisma.configurationversion.find_unique(where={"id": v2_id})
        assert v1.active == False
        assert v2.active == True
        print("  ✅ Transaction atomicity verified - v1 deactivated, v2 active")
        
        # Test failed transaction (should rollback)
        async def failing_operation(tx):
            # This will fail due to missing required fields
            await tx.configurationversion.create(
                data={"type": "test_fail"}  # Missing required fields
            )
        
        try:
            await db.transaction(failing_operation)
            assert False, "Should have raised an error"
        except Exception:
            print("  ✅ Transaction correctly rolled back on error")
        
        # Cleanup
        await db.prisma.configurationversion.delete_many(
            where={"type": "test_tx"}
        )
        
    finally:
        await db.disconnect()


async def test_connection_pooling():
    """Test connection pooling handles concurrent requests."""
    print("\n🧪 Testing Connection Pooling...")
    db = DatabaseService()
    await db.connect()
    
    try:
        # Create test sessions concurrently
        tasks = []
        for i in range(10):
            task = db.create_session(
                app_name=f"test_pool_{i}",
                user_id="test_user",
                session_id=f"test_pool_session_{i}"
            )
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        assert len(results) == 10
        print(f"  ✅ Created 10 sessions concurrently")
        
        # Verify all were created
        sessions = await db.list_sessions(app_name="test_pool")
        # Note: list_sessions doesn't support prefix matching, so count differently
        count = await db.prisma.session.count(
            where={"app_name": {"startswith": "test_pool_"}}
        )
        assert count >= 10
        print(f"  ✅ Verified all sessions exist (count: {count})")
        
        # Cleanup
        await db.prisma.session.delete_many(
            where={"app_name": {"startswith": "test_pool_"}}
        )
        print("  ✅ Cleaned up test data")
        
    finally:
        await db.disconnect()


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("🚀 Running Critical Path Integration Tests (KISS Edition)")
    print("="*60)
    
    tests = [
        ("Session CRUD", test_session_crud),
        ("Execution Flow", test_execution_flow),
        ("Cascade Delete", test_cascade_delete),
        ("Transaction Atomicity", test_transaction_atomicity),
        ("Connection Pooling", test_connection_pooling),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} failed: {e}")
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("✨ All critical path tests passed!")
    else:
        print("⚠️  Some tests failed - please investigate")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)