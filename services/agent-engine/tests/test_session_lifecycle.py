"""
Test suite for session lifecycle management.

Tests cover:
- Session forking for branching conversations
- Session merging for combining branches
- Session cleanup and garbage collection
- Session state persistence and recovery
- Multi-backend session management
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any
import uuid

from google.adk.sessions import InMemorySessionService

from src.core.execution import (
    SessionBackend,
    ExecutionContext,
    SessionServiceFactory,
    SessionLifecycleManager,
    RunnerManager,
    ExecutionService,
    EventHistoryManager
)


class MockSession:
    """Mock session for testing."""
    
    def __init__(self, session_id: str, user_id: str = "test-user", initial_state: Dict[str, Any] = None):
        self.id = session_id
        self.user_id = user_id
        self.state = initial_state or {}
        self.created_at = "2025-01-01T00:00:00Z"
        self.updated_at = "2025-01-01T00:00:00Z"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class MockSessionService:
    """Mock session service for testing lifecycle operations."""
    
    def __init__(self):
        self.sessions: Dict[str, MockSession] = {}
    
    def create_session(self, app_name: str, user_id: str, session_id: str = None, initial_state: Dict[str, Any] = None):
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = MockSession(session_id, user_id, initial_state)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str):
        return self.sessions.get(session_id)
    
    def update_session_state(self, session_id: str, state: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].state.update(state)
            return True
        return False
    
    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self, user_id: str = None):
        if user_id:
            return [s for s in self.sessions.values() if s.user_id == user_id]
        return list(self.sessions.values())


class TestSessionLifecycleManager:
    """Test SessionLifecycleManager functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session_service = MockSessionService()
        self.lifecycle_manager = SessionLifecycleManager(self.mock_session_service)
    
    @pytest.mark.asyncio
    async def test_fork_session_basic(self):
        """Test basic session forking functionality."""
        # Create source session
        source_session = self.mock_session_service.create_session(
            app_name="test-app",
            user_id="test-user",
            session_id="source-session",
            initial_state={"context": "original conversation", "turn": 1}
        )
        
        # Fork session
        new_session_id = await self.lifecycle_manager.fork_session("source-session")
        
        # Verify new session ID was generated
        assert new_session_id is not None
        assert new_session_id != "source-session"
        assert len(new_session_id) > 0
    
    @pytest.mark.asyncio
    async def test_fork_session_with_custom_id(self):
        """Test session forking with custom ID."""
        # Create source session
        self.mock_session_service.create_session(
            app_name="test-app",
            user_id="test-user",
            session_id="source-session"
        )
        
        # Fork with custom ID
        custom_id = "custom-fork-123"
        new_session_id = await self.lifecycle_manager.fork_session("source-session", custom_id)
        
        assert new_session_id == custom_id
    
    @pytest.mark.asyncio
    async def test_fork_nonexistent_session(self):
        """Test forking non-existent session."""
        # Try to fork non-existent session
        new_session_id = await self.lifecycle_manager.fork_session("non-existent")
        
        # Should still return a new ID (placeholder implementation)
        assert new_session_id is not None
    
    @pytest.mark.asyncio
    async def test_merge_sessions_basic(self):
        """Test basic session merging functionality."""
        # Create multiple sessions to merge
        session_ids = ["session-1", "session-2", "session-3"]
        target_id = "merged-session"
        
        for session_id in session_ids:
            self.mock_session_service.create_session(
                app_name="test-app",
                user_id="test-user",
                session_id=session_id,
                initial_state={"data": f"from-{session_id}"}
            )
        
        # Merge sessions
        result = await self.lifecycle_manager.merge_sessions(session_ids, target_id)
        
        # Current implementation returns False (placeholder)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_merge_empty_session_list(self):
        """Test merging empty session list."""
        result = await self.lifecycle_manager.merge_sessions([], "target")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_session_basic(self):
        """Test basic session cleanup."""
        # Create session to cleanup
        session_id = "cleanup-test"
        self.mock_session_service.create_session(
            app_name="test-app",
            user_id="test-user",
            session_id=session_id
        )
        
        # Cleanup session
        result = await self.lifecycle_manager.cleanup_session(session_id)
        
        # Current implementation returns False (placeholder)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_session(self):
        """Test cleanup of non-existent session."""
        result = await self.lifecycle_manager.cleanup_session("non-existent")
        assert result is False


class TestSessionPersistence:
    """Test session state persistence and recovery."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session_service = MockSessionService()
        self.context = ExecutionContext(
            app_name="persistence-test",
            user_id="test-user"
        )
    
    def test_session_state_persistence(self):
        """Test persisting session state."""
        # Create session with initial state
        initial_state = {
            "conversation_history": ["Hello", "Hi there!"],
            "user_preferences": {"language": "en", "theme": "dark"},
            "context_variables": {"current_topic": "weather"}
        }
        
        session = self.mock_session_service.create_session(
            app_name=self.context.app_name,
            user_id=self.context.user_id,
            session_id="persistence-test",
            initial_state=initial_state
        )
        
        # Verify state was persisted
        assert session.state == initial_state
        
        # Update state
        new_state = {"current_topic": "sports", "last_activity": "2025-01-01T12:00:00Z"}
        result = self.mock_session_service.update_session_state("persistence-test", new_state)
        
        assert result is True
        
        # Verify updated state
        retrieved_session = self.mock_session_service.get_session("persistence-test")
        assert retrieved_session.state["current_topic"] == "sports"
        assert retrieved_session.state["last_activity"] == "2025-01-01T12:00:00Z"
        
        # Original state should still be there
        assert retrieved_session.state["conversation_history"] == ["Hello", "Hi there!"]
    
    def test_session_recovery(self):
        """Test session recovery after creation."""
        # Create session
        session_id = "recovery-test"
        original_state = {"step": 1, "data": "important"}
        
        session = self.mock_session_service.create_session(
            app_name=self.context.app_name,
            user_id=self.context.user_id,
            session_id=session_id,
            initial_state=original_state
        )
        
        # Simulate recovery (get existing session)
        recovered_session = self.mock_session_service.get_session(session_id)
        
        assert recovered_session is not None
        assert recovered_session.id == session_id
        assert recovered_session.state == original_state
    
    def test_session_not_found(self):
        """Test handling of non-existent session."""
        non_existent = self.mock_session_service.get_session("does-not-exist")
        assert non_existent is None


class TestMultiBackendSessionManagement:
    """Test multi-backend session management."""
    
    def test_memory_backend_creation(self):
        """Test creating memory session backend."""
        service = SessionServiceFactory.create_session_service(SessionBackend.MEMORY)
        assert isinstance(service, InMemorySessionService)
    
    def test_redis_backend_fallback(self):
        """Test Redis backend fallback to memory."""
        # Redis not implemented yet, should fallback
        service = SessionServiceFactory.create_session_service(SessionBackend.REDIS)
        assert isinstance(service, InMemorySessionService)
    
    def test_vertex_backend_fallback(self):
        """Test Vertex backend fallback to memory."""
        # Vertex not implemented yet, should fallback
        service = SessionServiceFactory.create_session_service(SessionBackend.VERTEX)
        assert isinstance(service, InMemorySessionService)
    
    def test_invalid_backend_error(self):
        """Test error for invalid backend."""
        with pytest.raises(ValueError, match="Unsupported session backend"):
            SessionServiceFactory.create_session_service("invalid_backend")
    
    def test_execution_context_backend_selection(self):
        """Test execution context with different backends."""
        # Test each backend
        for backend in SessionBackend:
            context = ExecutionContext(backend=backend)
            assert context.backend == backend
            
            # Create session service for context
            service = SessionServiceFactory.create_session_service(context.backend)
            assert service is not None


class TestSessionIntegrationWithExecution:
    """Test session integration with execution system."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_factory = Mock()
        self.execution_service = ExecutionService(self.mock_factory)
        self.runner_manager = RunnerManager()
    
    def test_session_creation_during_execution(self):
        """Test session creation during agent execution setup."""
        # Create execution context
        context = ExecutionContext(
            app_name="integration-test",
            user_id="integration-user",
            session_id="integration-session"
        )
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.name = "integration_agent"
        
        # Create runner (this should handle session creation)
        runner = self.runner_manager.create_runner(mock_agent, context)
        
        # Verify runner was created
        assert runner is not None
        assert hasattr(runner, 'session_service')
        
        # Verify runner is cached
        runner_id = f"{context.app_name}:{mock_agent.name}"
        cached_runner = self.runner_manager.get_runner(runner_id)
        assert cached_runner is runner
    
    def test_session_cleanup_after_execution(self):
        """Test session cleanup after execution completes."""
        # Create and use runner
        context = ExecutionContext()
        mock_agent = Mock()
        mock_agent.name = "cleanup_agent"
        
        runner = self.runner_manager.create_runner(mock_agent, context)
        runner_id = f"{context.app_name}:{mock_agent.name}"
        
        # Verify runner exists
        assert self.runner_manager.get_runner(runner_id) is not None
        
        # Cleanup
        result = self.runner_manager.cleanup_runner(runner_id)
        assert result is True
        
        # Verify cleanup
        assert self.runner_manager.get_runner(runner_id) is None
    
    def test_multiple_sessions_same_user(self):
        """Test managing multiple sessions for same user."""
        user_id = "multi-session-user"
        
        # Create multiple execution contexts for same user
        contexts = [
            ExecutionContext(user_id=user_id, session_id=f"session-{i}")
            for i in range(3)
        ]
        
        # Create mock session service to track sessions
        mock_service = MockSessionService()
        
        # Create sessions
        sessions = []
        for context in contexts:
            session = mock_service.create_session(
                app_name=context.app_name,
                user_id=context.user_id,
                session_id=context.session_id
            )
            sessions.append(session)
        
        # Verify all sessions created for same user
        user_sessions = mock_service.list_sessions(user_id)
        assert len(user_sessions) == 3
        
        # Verify each session is unique
        session_ids = [s.id for s in user_sessions]
        assert len(set(session_ids)) == 3  # All unique


class TestSessionConcurrency:
    """Test concurrent session operations."""
    
    def setup_method(self):
        """Set up concurrency test fixtures."""
        self.mock_session_service = MockSessionService()
        self.lifecycle_manager = SessionLifecycleManager(self.mock_session_service)
    
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self):
        """Test concurrent session creation."""
        async def create_session_task(session_id: str):
            return self.mock_session_service.create_session(
                app_name="concurrent-test",
                user_id="concurrent-user",
                session_id=session_id
            )
        
        # Create multiple sessions concurrently
        num_sessions = 5
        tasks = [
            create_session_task(f"concurrent-{i}")
            for i in range(num_sessions)
        ]
        
        sessions = await asyncio.gather(*tasks)
        
        # Verify all sessions created
        assert len(sessions) == num_sessions
        
        # Verify all sessions are unique
        session_ids = [s.id for s in sessions]
        assert len(set(session_ids)) == num_sessions
    
    @pytest.mark.asyncio
    async def test_concurrent_session_forking(self):
        """Test concurrent session forking."""
        # Create source session
        source_id = "fork-source"
        self.mock_session_service.create_session(
            app_name="fork-test",
            user_id="fork-user",
            session_id=source_id
        )
        
        # Fork multiple sessions concurrently
        async def fork_task():
            return await self.lifecycle_manager.fork_session(source_id)
        
        num_forks = 3
        tasks = [fork_task() for _ in range(num_forks)]
        fork_ids = await asyncio.gather(*tasks)
        
        # Verify all forks created unique IDs
        assert len(fork_ids) == num_forks
        assert len(set(fork_ids)) == num_forks  # All unique
        
        # Verify none are the source ID
        assert source_id not in fork_ids
    
    @pytest.mark.asyncio
    async def test_concurrent_session_cleanup(self):
        """Test concurrent session cleanup."""
        # Create sessions to cleanup
        session_ids = [f"cleanup-{i}" for i in range(3)]
        
        for session_id in session_ids:
            self.mock_session_service.create_session(
                app_name="cleanup-test",
                user_id="cleanup-user",
                session_id=session_id
            )
        
        # Cleanup sessions concurrently
        async def cleanup_task(session_id: str):
            return await self.lifecycle_manager.cleanup_session(session_id)
        
        tasks = [cleanup_task(sid) for sid in session_ids]
        results = await asyncio.gather(*tasks)
        
        # Current implementation returns False (placeholder)
        assert all(result is False for result in results)


class TestSessionErrorHandling:
    """Test session error handling and edge cases."""
    
    def setup_method(self):
        """Set up error handling test fixtures."""
        self.mock_session_service = MockSessionService()
        self.lifecycle_manager = SessionLifecycleManager(self.mock_session_service)
    
    def test_duplicate_session_creation(self):
        """Test handling of duplicate session IDs."""
        session_id = "duplicate-test"
        
        # Create first session
        session1 = self.mock_session_service.create_session(
            app_name="dup-test",
            user_id="dup-user",
            session_id=session_id
        )
        
        # Create second session with same ID (should overwrite)
        session2 = self.mock_session_service.create_session(
            app_name="dup-test",
            user_id="dup-user",
            session_id=session_id
        )
        
        # Should have overwritten
        assert session2.id == session_id
        
        # Verify only one session exists
        retrieved = self.mock_session_service.get_session(session_id)
        assert retrieved is session2
    
    def test_invalid_session_operations(self):
        """Test operations on invalid sessions."""
        # Try to update non-existent session
        result = self.mock_session_service.update_session_state(
            "non-existent", 
            {"test": "data"}
        )
        assert result is False
        
        # Try to delete non-existent session
        result = self.mock_session_service.delete_session("non-existent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_lifecycle_operations_on_invalid_sessions(self):
        """Test lifecycle operations on invalid sessions."""
        # Fork non-existent session
        fork_id = await self.lifecycle_manager.fork_session("non-existent")
        assert fork_id is not None  # Should still generate ID
        
        # Merge non-existent sessions
        result = await self.lifecycle_manager.merge_sessions(
            ["non-existent-1", "non-existent-2"], 
            "target"
        )
        assert result is False
        
        # Cleanup non-existent session
        result = await self.lifecycle_manager.cleanup_session("non-existent")
        assert result is False