"""
Test suite for streaming functionality with event iteration.

Tests cover:
- Event iteration patterns from run_async
- Streaming executor functionality
- Event filtering and transformation
- Partial response handling
- Final response detection
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import List

from google.adk.events import Event
from google.adk.runners import InMemoryRunner

from src.core.execution import (
    StreamingExecutor,
    ExecutionContext,
    ExecutionResult,
    ExecutionService,
    EventHistoryManager
)


class MockStreamingAgent:
    """Mock agent that generates streaming events."""
    
    def __init__(self, name: str = "streaming_agent"):
        self.name = name
    
    async def _run_async_impl(self, ctx):
        """Generate streaming events."""
        # Start event
        yield Event(type="agent_turn_start", data={"agent": self.name})
        
        # Partial content events
        yield Event(type="text", data={"content": "Hello "})
        yield Event(type="text", data={"content": "there! "})
        yield Event(type="text", data={"content": "How "})
        yield Event(type="text", data={"content": "can "})
        yield Event(type="text", data={"content": "I help?"})
        
        # Final event
        yield Event(type="agent_turn_end", data={"final_content": "Hello there! How can I help?"})


class TestStreamingExecution:
    """Test streaming execution patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.context = ExecutionContext(
            app_name="streaming-test",
            user_id="test-user",
            enable_streaming=True
        )
        
        # Create mock runner with streaming events
        self.mock_runner = Mock(spec=InMemoryRunner)
        self.mock_runner.run_async = AsyncMock()
        
        self.executor = StreamingExecutor(self.mock_runner, self.context)
    
    @pytest.mark.asyncio
    async def test_basic_streaming(self):
        """Test basic streaming event iteration."""
        # Mock streaming events
        streaming_events = [
            Event(author="streaming_agent", content="Starting"),
            Event(author="streaming_agent", content="Hello "),
            Event(author="streaming_agent", content="World!"),
            Event(author="streaming_agent", content="Complete")
        ]
        
        async def mock_run_async(*args):
            for event in streaming_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Collect streamed events
        collected_events = []
        async for event in self.executor.execute_stream("Test input"):
            collected_events.append(event)
        
        assert len(collected_events) == 4
        assert collected_events[0].type == "start"
        assert collected_events[1].data["content"] == "Hello "
        assert collected_events[2].data["content"] == "World!"
        assert collected_events[3].type == "end"
    
    @pytest.mark.asyncio
    async def test_partial_content_streaming(self):
        """Test handling of partial content events."""
        # Mock partial streaming events
        partial_events = [
            Event(type="text", data={"content": "The "}),
            Event(type="text", data={"content": "quick "}),
            Event(type="text", data={"content": "brown "}),
            Event(type="text", data={"content": "fox"})
        ]
        
        async def mock_run_async(*args):
            for event in partial_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Collect and concatenate partial content
        full_content = ""
        async for event in self.executor.execute_stream("Test input"):
            if event.type == "text" and "content" in event.data:
                full_content += event.data["content"]
        
        assert full_content == "The quick brown fox"
    
    @pytest.mark.asyncio
    async def test_final_response_detection(self):
        """Test detection of final response events."""
        # Mock events with final response marker
        events_with_final = [
            Event(type="text", data={"content": "Response text"}),
            Mock(type="final", data={"content": "Final response"})
        ]
        
        # Add is_final_response method to mock final event
        events_with_final[1].is_final_response = Mock(return_value=True)
        
        async def mock_run_async(*args):
            for event in events_with_final:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Check final response detection
        final_detected = False
        async for event in self.executor.execute_stream("Test input"):
            if hasattr(event, 'is_final_response') and event.is_final_response():
                final_detected = True
                break
        
        assert final_detected is True
    
    @pytest.mark.asyncio
    async def test_streaming_error_handling(self):
        """Test error handling in streaming."""
        # Mock runner to raise exception during streaming
        async def mock_run_async_with_error(*args):
            yield Event(type="start", data={"message": "Starting"})
            raise Exception("Streaming error occurred")
        
        self.mock_runner.run_async.side_effect = mock_run_async_with_error
        
        # Collect events including error
        events = []
        async for event in self.executor.execute_stream("Test input"):
            events.append(event)
        
        # Should have start event and error event
        assert len(events) == 2
        assert events[0].type == "start"
        assert events[1].type == "error"
        assert "Streaming error occurred" in str(events[1].data)
    
    @pytest.mark.asyncio
    async def test_streaming_timeout(self):
        """Test streaming with slow events."""
        async def slow_streaming(*args):
            yield Event(type="start", data={"message": "Starting"})
            await asyncio.sleep(0.1)  # Simulate slow processing
            yield Event(type="text", data={"content": "Slow response"})
        
        self.mock_runner.run_async.side_effect = slow_streaming
        
        # Stream with timeout consideration
        events = []
        start_time = asyncio.get_event_loop().time()
        
        async for event in self.executor.execute_stream("Test input"):
            events.append(event)
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        assert len(events) == 2
        assert duration >= 0.1  # Should take at least the sleep time


class TestStreamingIntegration:
    """Test streaming integration with ExecutionService."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_factory = Mock()
        self.execution_service = ExecutionService(self.mock_factory)
        self.context = ExecutionContext(enable_streaming=True)
    
    @pytest.mark.asyncio
    async def test_stream_agent_from_spec(self):
        """Test streaming agent execution from specification."""
        # Create mock agent that returns events
        mock_agent = Mock()
        self.mock_factory.build_agent_from_spec.return_value = mock_agent
        
        # Mock streaming by patching the internal method
        test_events = [
            Event(type="start", data={"message": "Starting spec execution"}),
            Event(type="text", data={"content": "Streaming from spec"}),
            Event(type="end", data={"message": "Spec execution complete"})
        ]
        
        async def mock_stream_execution(*args):
            for event in test_events:
                yield event
        
        # Patch the stream_agent_execution method
        original_method = self.execution_service.stream_agent_execution
        self.execution_service.stream_agent_execution = mock_stream_execution
        
        try:
            # Stream from specification
            events = []
            async for event in self.execution_service.stream_agent_from_spec(
                "test_spec", 
                "Stream test input",
                self.context
            ):
                events.append(event)
            
            assert len(events) == 3
            assert events[0].type == "start"
            assert events[1].data["content"] == "Streaming from spec"
            assert events[2].type == "end"
            
            # Verify factory was called
            self.mock_factory.build_agent_from_spec.assert_called_once()
            
        finally:
            # Restore original method
            self.execution_service.stream_agent_execution = original_method


class TestEventFiltering:
    """Test event filtering and transformation capabilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.context = ExecutionContext()
        self.mock_runner = Mock(spec=InMemoryRunner)
        self.mock_runner.run_async = AsyncMock()
        self.executor = StreamingExecutor(self.mock_runner, self.context)
    
    @pytest.mark.asyncio
    async def test_filter_text_events(self):
        """Test filtering only text events."""
        # Mixed event types
        mixed_events = [
            Event(type="start", data={"message": "Starting"}),
            Event(type="text", data={"content": "Hello"}),
            Event(type="metadata", data={"info": "Some metadata"}),
            Event(type="text", data={"content": " World"}),
            Event(type="end", data={"message": "Done"})
        ]
        
        async def mock_run_async(*args):
            for event in mixed_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Filter only text events
        text_content = ""
        async for event in self.executor.execute_stream("Test input"):
            if event.type == "text" and "content" in event.data:
                text_content += event.data["content"]
        
        assert text_content == "Hello World"
    
    @pytest.mark.asyncio
    async def test_transform_events(self):
        """Test transforming events during streaming."""
        # Events to transform
        raw_events = [
            Event(type="text", data={"content": "hello world"}),
            Event(type="text", data={"content": "this is a test"})
        ]
        
        async def mock_run_async(*args):
            for event in raw_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Transform events (uppercase content)
        transformed_content = []
        async for event in self.executor.execute_stream("Test input"):
            if event.type == "text" and "content" in event.data:
                transformed = event.data["content"].upper()
                transformed_content.append(transformed)
        
        assert transformed_content == ["HELLO WORLD", "THIS IS A TEST"]


class TestEventHistoryIntegration:
    """Test event history integration with streaming."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.history_manager = EventHistoryManager()
        self.session_id = "streaming-session"
        
        self.context = ExecutionContext(session_id=self.session_id)
        self.mock_runner = Mock(spec=InMemoryRunner)
        self.mock_runner.run_async = AsyncMock()
        self.executor = StreamingExecutor(self.mock_runner, self.context)
    
    @pytest.mark.asyncio
    async def test_capture_streaming_history(self):
        """Test capturing streaming events in history."""
        # Events to stream and capture
        stream_events = [
            Event(type="user_input", data={"content": "User question"}),
            Event(type="agent_thinking", data={"message": "Processing..."}),
            Event(type="text", data={"content": "Agent response"}),
            Event(type="agent_turn_end", data={"complete": True})
        ]
        
        async def mock_run_async(*args):
            for event in stream_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_run_async
        
        # Stream and capture in history
        async for event in self.executor.execute_stream("Test input"):
            self.history_manager.add_event(self.session_id, event)
        
        # Verify history was captured
        history = self.history_manager.get_history(self.session_id)
        assert len(history) == 4
        
        # Verify event types in correct order
        assert history[0].type == "user_input"
        assert history[1].type == "agent_thinking"
        assert history[2].type == "text"
        assert history[3].type == "agent_turn_end"
    
    @pytest.mark.asyncio
    async def test_conversation_continuity(self):
        """Test maintaining conversation history across multiple streams."""
        # First conversation turn
        first_events = [
            Event(type="text", data={"content": "First response"}),
            Event(type="end", data={"turn": 1})
        ]
        
        # Second conversation turn  
        second_events = [
            Event(type="text", data={"content": "Second response"}),
            Event(type="end", data={"turn": 2})
        ]
        
        # First stream
        async def first_stream(*args):
            for event in first_events:
                yield event
        
        self.mock_runner.run_async.side_effect = first_stream
        
        async for event in self.executor.execute_stream("First input"):
            self.history_manager.add_event(self.session_id, event)
        
        # Second stream
        async def second_stream(*args):
            for event in second_events:
                yield event
        
        self.mock_runner.run_async.side_effect = second_stream
        
        async for event in self.executor.execute_stream("Second input"):
            self.history_manager.add_event(self.session_id, event)
        
        # Verify complete conversation history
        history = self.history_manager.get_history(self.session_id)
        assert len(history) == 4  # 2 events from each turn
        
        # Verify chronological order
        assert history[0].data["content"] == "First response"
        assert history[1].data["turn"] == 1
        assert history[2].data["content"] == "Second response"
        assert history[3].data["turn"] == 2


class TestPerformanceAndScaling:
    """Test performance aspects of streaming."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.context = ExecutionContext()
        self.mock_runner = Mock(spec=InMemoryRunner)
        self.mock_runner.run_async = AsyncMock()
        self.executor = StreamingExecutor(self.mock_runner, self.context)
    
    @pytest.mark.asyncio
    async def test_large_stream_handling(self):
        """Test handling large number of events."""
        # Generate large number of events
        num_events = 1000
        large_events = [
            Event(type="text", data={"content": f"Event {i}"})
            for i in range(num_events)
        ]
        
        async def mock_large_stream(*args):
            for event in large_events:
                yield event
        
        self.mock_runner.run_async.side_effect = mock_large_stream
        
        # Process large stream
        event_count = 0
        async for event in self.executor.execute_stream("Large stream test"):
            event_count += 1
        
        assert event_count == num_events
    
    @pytest.mark.asyncio
    async def test_concurrent_streaming(self):
        """Test concurrent streaming execution."""
        # Create multiple streaming tasks
        async def single_stream_task():
            events = [
                Event(type="text", data={"content": "Concurrent event"})
            ]
            
            async def mock_stream(*args):
                for event in events:
                    yield event
            
            # Create separate executor for this task
            local_runner = Mock(spec=InMemoryRunner)
            local_runner.run_async = AsyncMock(side_effect=mock_stream)
            local_executor = StreamingExecutor(local_runner, self.context)
            
            count = 0
            async for event in local_executor.execute_stream("Concurrent input"):
                count += 1
            return count
        
        # Run multiple concurrent streams
        num_concurrent = 5
        tasks = [single_stream_task() for _ in range(num_concurrent)]
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert all(result == 1 for result in results)
        assert len(results) == num_concurrent