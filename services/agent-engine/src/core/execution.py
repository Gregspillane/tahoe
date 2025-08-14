"""
Agent Execution Orchestration with InMemoryRunner Integration

This module provides the core execution infrastructure for running agents created by the
UniversalAgentFactory with ADK's InMemoryRunner. It supports streaming execution, 
multi-backend session management, and event-driven architecture.

Key ADK Patterns Implemented:
- InMemoryRunner for agent execution lifecycle
- Session service property access (not method call)
- Event iteration for streaming with run_async
- Multi-backend session support (memory, redis, vertex)
- Error recovery and resilience patterns

References:
- https://google.github.io/adk-docs/runtime/
- https://google.github.io/adk-docs/events/
- https://google.github.io/adk-docs/sessions/
"""

import asyncio
import logging
import time
from enum import Enum
from typing import AsyncIterator, Iterator, List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import uuid

from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.events import Event
from google.adk.agents import BaseAgent

from .composition import UniversalAgentFactory, AgentContext, AgentSpec

logger = logging.getLogger(__name__)


class SessionBackend(Enum):
    """Supported session backends for agent execution."""
    MEMORY = "memory"
    REDIS = "redis"
    VERTEX = "vertex"


@dataclass
class ExecutionContext:
    """Configuration for agent execution."""
    app_name: str = "agent-engine"
    user_id: str = "system"
    session_id: Optional[str] = None
    backend: SessionBackend = SessionBackend.MEMORY
    initial_state: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[float] = 300.0
    enable_streaming: bool = True
    trace_enabled: bool = False
    
    def __post_init__(self):
        """Generate session_id if not provided."""
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())


@dataclass
class ExecutionResult:
    """Result from agent execution."""
    session_id: str
    events: List[Event]
    final_content: Optional[str] = None
    execution_time_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamingExecutor:
    """Handles async event iteration and streaming from ADK runners."""
    
    def __init__(self, runner: InMemoryRunner, context: ExecutionContext):
        self.runner = runner
        self.context = context
        self.events: List[Event] = []
        
    async def execute_stream(self, input_data: Union[str, Dict[str, Any]]) -> AsyncIterator[Event]:
        """
        Execute agent with streaming event iteration.
        
        Implements proper ADK pattern:
        async for event in runner.run_async(user_id, session_id, input_data):
        """
        try:
            logger.debug(f"Starting streaming execution for session {self.context.session_id}")
            
            # ADK Pattern: Iterate through events from run_async
            async for event in self.runner.run_async(
                self.context.user_id, 
                self.context.session_id, 
                input_data
            ):
                self.events.append(event)
                logger.debug(f"Received event: {event.type if hasattr(event, 'type') else 'unknown'}")
                
                # Yield event for streaming
                yield event
                
                # Check for final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    logger.debug("Final response event received")
                    break
                    
        except Exception as e:
            logger.error(f"Streaming execution failed: {str(e)}")
            # Create error event
            error_event = Event(author="system", content=f"Error: {str(e)}")
            self.events.append(error_event)
            yield error_event
    
    async def execute_to_completion(self, input_data: Union[str, Dict[str, Any]]) -> ExecutionResult:
        """Execute agent to completion and return consolidated result."""
        start_time = time.time()
        events = []
        final_content = None
        error = None
        
        try:
            async for event in self.execute_stream(input_data):
                events.append(event)
                
                # Extract final content if available
                if hasattr(event, 'content') and event.content:
                    final_content = event.content
                elif hasattr(event, 'data') and isinstance(event.data, dict):
                    if 'content' in event.data:
                        final_content = event.data['content']
                    elif 'result' in event.data:
                        final_content = event.data['result']
                        
        except Exception as e:
            error = str(e)
            logger.error(f"Execution failed: {error}")
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return ExecutionResult(
            session_id=self.context.session_id,
            events=events,
            final_content=final_content,
            execution_time_ms=execution_time,
            success=error is None,
            error=error,
            metadata={
                "event_count": len(events),
                "backend": self.context.backend.value,
                "streaming": self.context.enable_streaming
            }
        )


class RunnerManager:
    """Manages InMemoryRunner instances and lifecycle."""
    
    def __init__(self):
        self._runners: Dict[str, InMemoryRunner] = {}
        
    def create_runner(self, agent: BaseAgent, context: ExecutionContext) -> InMemoryRunner:
        """
        Create InMemoryRunner for agent execution.
        
        ADK Pattern: InMemoryRunner(agent, app_name="app_name")
        """
        runner_id = f"{context.app_name}:{agent.name}"
        
        if runner_id in self._runners:
            logger.debug(f"Reusing existing runner for {runner_id}")
            return self._runners[runner_id]
        
        logger.debug(f"Creating new InMemoryRunner for {runner_id}")
        runner = InMemoryRunner(agent, app_name=context.app_name)
        
        # ADK Pattern: Access session_service as property (not method)
        session_service = runner.session_service
        logger.debug(f"Runner created with session service: {type(session_service).__name__}")
        
        self._runners[runner_id] = runner
        return runner
    
    def get_runner(self, runner_id: str) -> Optional[InMemoryRunner]:
        """Get existing runner by ID."""
        return self._runners.get(runner_id)
    
    def cleanup_runner(self, runner_id: str) -> bool:
        """Remove runner from cache."""
        if runner_id in self._runners:
            del self._runners[runner_id]
            logger.debug(f"Cleaned up runner: {runner_id}")
            return True
        return False
    
    def cleanup_all(self):
        """Clean up all runners."""
        count = len(self._runners)
        self._runners.clear()
        logger.debug(f"Cleaned up {count} runners")


class SessionServiceFactory:
    """Factory for creating different session service backends."""
    
    @staticmethod
    def create_session_service(backend: SessionBackend, **kwargs):
        """Create session service based on backend type."""
        if backend == SessionBackend.MEMORY:
            return InMemorySessionService()
        elif backend == SessionBackend.REDIS:
            # TODO: Implement RedisSessionService
            logger.warning("Redis session backend not yet implemented, falling back to memory")
            return InMemorySessionService()
        elif backend == SessionBackend.VERTEX:
            # TODO: Implement VertexSessionService
            logger.warning("Vertex session backend not yet implemented, falling back to memory")
            return InMemorySessionService()
        else:
            raise ValueError(f"Unsupported session backend: {backend}")


class ExecutionService:
    """Main execution service integrating with UniversalAgentFactory."""
    
    def __init__(self, agent_factory: UniversalAgentFactory):
        self.agent_factory = agent_factory
        self.runner_manager = RunnerManager()
        
    async def execute_agent_from_spec(
        self, 
        spec_name: str, 
        input_data: Union[str, Dict[str, Any]], 
        context: Optional[ExecutionContext] = None,
        agent_context: Optional[AgentContext] = None
    ) -> ExecutionResult:
        """Execute agent from specification name."""
        if context is None:
            context = ExecutionContext()
        
        if agent_context is None:
            agent_context = AgentContext()
            
        # Build agent from specification  
        agent = self.agent_factory.build_agent_from_dict(spec_name, agent_context.model_dump())
        
        return await self.execute_agent(agent, input_data, context)
    
    async def execute_agent(
        self, 
        agent: BaseAgent, 
        input_data: Union[str, Dict[str, Any]], 
        context: Optional[ExecutionContext] = None
    ) -> ExecutionResult:
        """Execute agent instance directly."""
        if context is None:
            context = ExecutionContext()
        
        # Create runner for agent
        runner = self.runner_manager.create_runner(agent, context)
        
        # Create session if needed
        await self._ensure_session(runner, context)
        
        # Create streaming executor
        executor = StreamingExecutor(runner, context)
        
        # Execute to completion
        return await executor.execute_to_completion(input_data)
    
    async def stream_agent_execution(
        self, 
        agent: BaseAgent, 
        input_data: Union[str, Dict[str, Any]], 
        context: Optional[ExecutionContext] = None
    ) -> AsyncIterator[Event]:
        """Stream agent execution events."""
        if context is None:
            context = ExecutionContext()
        
        # Create runner for agent
        runner = self.runner_manager.create_runner(agent, context)
        
        # Create session if needed
        await self._ensure_session(runner, context)
        
        # Create streaming executor
        executor = StreamingExecutor(runner, context)
        
        # Stream events
        async for event in executor.execute_stream(input_data):
            yield event
    
    async def stream_agent_from_spec(
        self, 
        spec_name: str, 
        input_data: Union[str, Dict[str, Any]], 
        context: Optional[ExecutionContext] = None,
        agent_context: Optional[AgentContext] = None
    ) -> AsyncIterator[Event]:
        """Stream agent execution from specification name."""
        if context is None:
            context = ExecutionContext()
        
        if agent_context is None:
            agent_context = AgentContext()
            
        # Build agent from specification  
        agent = self.agent_factory.build_agent_from_dict(spec_name, agent_context.model_dump())
        
        # Stream execution
        async for event in self.stream_agent_execution(agent, input_data, context):
            yield event
    
    async def _ensure_session(self, runner: InMemoryRunner, context: ExecutionContext):
        """Ensure session exists for execution context."""
        # ADK Pattern: Access session_service as property
        session_service = runner.session_service
        
        try:
            # Try to get existing session
            session = session_service.get_session(context.session_id)
            if session is None:
                # Create new session with required parameters
                session = session_service.create_session(
                    app_name=context.app_name,
                    user_id=context.user_id,
                    session_id=context.session_id,
                    initial_state=context.initial_state
                )
                logger.debug(f"Created new session: {context.session_id}")
            else:
                logger.debug(f"Using existing session: {context.session_id}")
        except Exception as e:
            logger.error(f"Session creation/retrieval failed: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up execution service resources."""
        self.runner_manager.cleanup_all()


# Session lifecycle management functions for future implementation
class SessionLifecycleManager:
    """Manages session forking, merging, and cleanup operations."""
    
    def __init__(self, session_service):
        self.session_service = session_service
    
    async def fork_session(self, source_session_id: str, new_session_id: Optional[str] = None) -> str:
        """Fork a session for branching conversations."""
        # TODO: Implement session forking
        if new_session_id is None:
            new_session_id = str(uuid.uuid4())
        logger.warning("Session forking not yet implemented")
        return new_session_id
    
    async def merge_sessions(self, session_ids: List[str], target_session_id: str) -> bool:
        """Merge multiple sessions into target session."""
        # TODO: Implement session merging
        logger.warning("Session merging not yet implemented")
        return False
    
    async def cleanup_session(self, session_id: str) -> bool:
        """Clean up session and release resources."""
        # TODO: Implement session cleanup
        logger.warning("Session cleanup not yet implemented")
        return False


# Error recovery and resilience patterns
class ExecutionResilience:
    """Implements error recovery and resilience patterns for agent execution."""
    
    @staticmethod
    async def with_retry(
        coro_func, 
        max_retries: int = 3, 
        base_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """Execute coroutine with exponential backoff retry."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await coro_func()
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = base_delay * (backoff_factor ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_retries + 1} attempts failed")
        
        raise last_error
    
    @staticmethod
    async def with_timeout(coro_func, timeout_seconds: float):
        """Execute coroutine with timeout."""
        try:
            return await asyncio.wait_for(coro_func(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            logger.error(f"Execution timed out after {timeout_seconds} seconds")
            raise


# Event system integration for conversation history
class EventHistoryManager:
    """Manages conversation history through events."""
    
    def __init__(self):
        self.event_history: Dict[str, List[Event]] = {}
    
    def add_event(self, session_id: str, event: Event):
        """Add event to session history."""
        if session_id not in self.event_history:
            self.event_history[session_id] = []
        self.event_history[session_id].append(event)
    
    def get_history(self, session_id: str) -> List[Event]:
        """Get event history for session."""
        return self.event_history.get(session_id, [])
    
    def clear_history(self, session_id: str) -> bool:
        """Clear event history for session."""
        if session_id in self.event_history:
            del self.event_history[session_id]
            return True
        return False