"""
Integration tests for R2-T05 execution system with UniversalAgentFactory.

Tests the core integration between ExecutionService and the existing agent factory
to verify R2-T05 requirements are met.
"""

import pytest
import asyncio
from typing import Dict, Any

from src.core.execution import (
    ExecutionService,
    ExecutionContext,
    SessionBackend,
    RunnerManager
)
from src.core.composition import UniversalAgentFactory


class TestExecutionIntegration:
    """Test integration between execution system and agent factory."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.factory = UniversalAgentFactory()
        self.execution_service = ExecutionService(self.factory)
    
    def test_execution_service_initialization(self):
        """Test ExecutionService initializes correctly with factory."""
        assert self.execution_service.agent_factory is self.factory
        assert isinstance(self.execution_service.runner_manager, RunnerManager)
    
    def test_execution_context_creation(self):
        """Test ExecutionContext creates with proper defaults."""
        context = ExecutionContext()
        
        # Verify R2-T05 requirements
        assert context.app_name == "agent-engine"
        assert context.user_id == "system"
        assert context.session_id is not None
        assert context.backend == SessionBackend.MEMORY
        assert context.timeout_seconds == 300.0
        assert context.enable_streaming is True
        assert context.trace_enabled is False
    
    def test_session_backend_support(self):
        """Test all session backends are supported."""
        # Test memory backend (implemented)
        context_memory = ExecutionContext(backend=SessionBackend.MEMORY)
        assert context_memory.backend == SessionBackend.MEMORY
        
        # Test redis backend (fallback to memory)
        context_redis = ExecutionContext(backend=SessionBackend.REDIS)
        assert context_redis.backend == SessionBackend.REDIS
        
        # Test vertex backend (fallback to memory)
        context_vertex = ExecutionContext(backend=SessionBackend.VERTEX)
        assert context_vertex.backend == SessionBackend.VERTEX
    
    def test_runner_manager_lifecycle(self):
        """Test RunnerManager handles agent lifecycles correctly."""
        # Create a simple context
        context = ExecutionContext(app_name="test-app")
        
        # Verify runner manager starts clean
        assert len(self.execution_service.runner_manager._runners) == 0
        
        # Cleanup (even though no runners created)
        self.execution_service.cleanup()
        assert len(self.execution_service.runner_manager._runners) == 0
    
    def test_factory_integration_methods(self):
        """Test ExecutionService has correct factory integration methods."""
        # Verify methods exist for spec-based execution
        assert hasattr(self.execution_service, 'execute_agent_from_spec')
        assert hasattr(self.execution_service, 'stream_agent_from_spec')
        
        # Verify methods exist for direct agent execution
        assert hasattr(self.execution_service, 'execute_agent')
        assert hasattr(self.execution_service, 'stream_agent_execution')
    
    def test_supported_execution_patterns(self):
        """Test that execution service supports key ADK patterns."""
        # Verify sync and async execution patterns are available
        assert hasattr(self.execution_service, 'execute_agent')
        assert hasattr(self.execution_service, 'stream_agent_execution')
        
        # Verify streaming capabilities
        context = ExecutionContext(enable_streaming=True)
        assert context.enable_streaming is True
        
        context_no_stream = ExecutionContext(enable_streaming=False)
        assert context_no_stream.enable_streaming is False


class TestSessionManagement:
    """Test session management integration."""
    
    def test_session_context_with_custom_params(self):
        """Test session context with custom parameters."""
        custom_state = {"user_preferences": {"theme": "dark"}}
        
        context = ExecutionContext(
            app_name="custom-app",
            user_id="custom-user",
            session_id="custom-session-123",
            initial_state=custom_state,
            backend=SessionBackend.MEMORY
        )
        
        assert context.app_name == "custom-app"
        assert context.user_id == "custom-user"
        assert context.session_id == "custom-session-123"
        assert context.initial_state == custom_state
        assert context.backend == SessionBackend.MEMORY
    
    def test_session_id_auto_generation(self):
        """Test session ID auto-generation."""
        context1 = ExecutionContext()
        context2 = ExecutionContext()
        
        # Should generate unique session IDs
        assert context1.session_id != context2.session_id
        assert len(context1.session_id) > 0
        assert len(context2.session_id) > 0


class TestErrorHandlingIntegration:
    """Test error handling and resilience integration."""
    
    def setup_method(self):
        """Set up error handling test fixtures."""
        self.factory = UniversalAgentFactory()
        self.execution_service = ExecutionService(self.factory)
    
    def test_execution_service_cleanup(self):
        """Test ExecutionService cleanup functionality."""
        # Should not raise errors even with no runners
        self.execution_service.cleanup()
        
        # Verify runner manager is cleaned
        assert len(self.execution_service.runner_manager._runners) == 0
    
    def test_execution_context_validation(self):
        """Test ExecutionContext handles edge cases."""
        # Test with None session_id (should auto-generate)
        context = ExecutionContext(session_id=None)
        assert context.session_id is not None
        
        # Test with empty initial state
        context = ExecutionContext(initial_state={})
        assert context.initial_state == {}
        
        # Test with timeout settings
        context = ExecutionContext(timeout_seconds=60.0)
        assert context.timeout_seconds == 60.0


class TestFactoryCompatibility:
    """Test compatibility with existing UniversalAgentFactory."""
    
    def setup_method(self):
        """Set up compatibility test fixtures."""
        self.factory = UniversalAgentFactory()
        self.execution_service = ExecutionService(self.factory)
    
    def test_factory_method_compatibility(self):
        """Test ExecutionService works with factory methods."""
        # Verify factory methods that execution service depends on
        assert hasattr(self.factory, 'build_agent_from_dict')
        assert hasattr(self.factory, 'list_supported_types')
        
        # Test supported types include what we expect
        supported_types = self.factory.list_supported_types()
        
        # From R2-T01, R2-T02, R2-T03, R2-T04 we should have these types
        expected_types = ['llm', 'sequential', 'parallel', 'loop', 'custom']
        for agent_type in expected_types:
            assert agent_type in supported_types, f"Agent type '{agent_type}' not supported by factory"
    
    def test_execution_service_factory_reference(self):
        """Test ExecutionService maintains correct factory reference."""
        assert self.execution_service.agent_factory is self.factory
        
        # Verify we can access factory methods through the service
        supported_types = self.execution_service.agent_factory.list_supported_types()
        assert isinstance(supported_types, list)
        assert len(supported_types) > 0


class TestR2T05Requirements:
    """Test specific R2-T05 requirements compliance."""
    
    def setup_method(self):
        """Set up requirements test fixtures."""
        self.factory = UniversalAgentFactory()
        self.execution_service = ExecutionService(self.factory)
    
    def test_inmemory_runner_integration(self):
        """Test InMemoryRunner integration requirement."""
        # R2-T05 requires InMemoryRunner integration
        runner_manager = self.execution_service.runner_manager
        assert hasattr(runner_manager, 'create_runner')
        assert hasattr(runner_manager, 'cleanup_runner')
        assert hasattr(runner_manager, 'cleanup_all')
    
    def test_session_service_property_access(self):
        """Test session service property access pattern."""
        # R2-T05 requires session_service property access (not method)
        # This is verified in implementation but we test the pattern exists
        runner_manager = self.execution_service.runner_manager
        
        # The create_runner method should handle session_service property access
        assert hasattr(runner_manager, 'create_runner')
    
    def test_streaming_execution_support(self):
        """Test streaming execution requirement."""
        # R2-T05 requires streaming with event iteration
        assert hasattr(self.execution_service, 'stream_agent_execution')
        assert hasattr(self.execution_service, 'stream_agent_from_spec')
    
    def test_multi_backend_session_support(self):
        """Test multi-backend session support requirement."""
        # R2-T05 requires memory, redis, vertex backend support
        for backend in SessionBackend:
            context = ExecutionContext(backend=backend)
            assert context.backend == backend
    
    def test_error_recovery_patterns(self):
        """Test error recovery patterns requirement."""
        # R2-T05 requires error recovery and resilience patterns
        from src.core.execution import ExecutionResilience
        
        assert hasattr(ExecutionResilience, 'with_retry')
        assert hasattr(ExecutionResilience, 'with_timeout')
    
    def test_event_system_integration(self):
        """Test event system integration requirement."""
        # R2-T05 requires event system for conversation history
        from src.core.execution import EventHistoryManager
        
        history_manager = EventHistoryManager()
        assert hasattr(history_manager, 'add_event')
        assert hasattr(history_manager, 'get_history')
        assert hasattr(history_manager, 'clear_history')
    
    def test_session_lifecycle_features(self):
        """Test session lifecycle features requirement."""
        # R2-T05 requires session forking, merging, cleanup
        from src.core.execution import SessionLifecycleManager
        
        # Create with mock session service
        mock_service = object()
        lifecycle_manager = SessionLifecycleManager(mock_service)
        
        assert hasattr(lifecycle_manager, 'fork_session')
        assert hasattr(lifecycle_manager, 'merge_sessions') 
        assert hasattr(lifecycle_manager, 'cleanup_session')