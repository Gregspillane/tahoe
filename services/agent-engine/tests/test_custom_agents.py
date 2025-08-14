"""
Comprehensive tests for custom agents functionality.
Tests R2-T04: Custom Agents implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile
import yaml

# Import the components we're testing
from src.core.composition import UniversalAgentFactory, AgentSpec, AgentContext, SpecificationError
from src.core.custom_agents import (
    AdaptiveOrchestrator,
    ConditionalRouter,
    StatefulWorkflow,
    BUILT_IN_CUSTOM_AGENTS,
    register_built_in_agents
)

# Real ADK imports - no fallbacks
from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext


class MockSession:
    """Mock session for testing"""
    def __init__(self):
        self.state = {}


# Only mark specific async tests with @pytest.mark.asyncio


class TestUniversalAgentFactoryCustomSupport:
    """Test custom agent support in UniversalAgentFactory."""
    
    def setup_method(self):
        """Set up test factory."""
        self.factory = UniversalAgentFactory()
    
    def test_factory_has_custom_registry(self):
        """Test that factory initializes with custom registry."""
        assert hasattr(self.factory, 'custom_registry')
        assert isinstance(self.factory.custom_registry, dict)
    
    def test_built_in_agents_registered(self):
        """Test that built-in custom agents are automatically registered."""
        # Built-in agents should be registered during factory initialization
        custom_agents = self.factory.list_custom_agents()
        expected_agents = ["AdaptiveOrchestrator", "ConditionalRouter", "StatefulWorkflow"]
        
        for agent_name in expected_agents:
            assert agent_name in custom_agents, f"Built-in agent {agent_name} not registered"
    
    def test_register_custom_agent_success(self):
        """Test successful custom agent registration."""
        class TestCustomAgent(BaseAgent):
            async def _run_async_impl(self, ctx):
                yield Event(type="test", data="success")
        
        self.factory.register_custom_agent("TestAgent", TestCustomAgent)
        
        assert "TestAgent" in self.factory.custom_registry
        assert self.factory.custom_registry["TestAgent"] == TestCustomAgent
    
    def test_register_custom_agent_invalid_inheritance(self):
        """Test registration fails for non-BaseAgent classes."""
        class InvalidAgent:
            pass
        
        with pytest.raises(ValueError, match="must inherit from BaseAgent"):
            self.factory.register_custom_agent("InvalidAgent", InvalidAgent)
    
    def test_register_custom_agent_missing_method(self):
        """Test registration fails when _run_async_impl is missing."""
        class IncompleteAgent(BaseAgent):
            pass
        
        with pytest.raises(ValueError, match="must override _run_async_impl method"):
            self.factory.register_custom_agent("IncompleteAgent", IncompleteAgent)
    
    def test_build_custom_agent_success(self):
        """Test successful custom agent building."""
        class TestCustomAgent(BaseAgent):
            def __init__(self, name, test_param=None, **kwargs):
                super().__init__(name=name, **kwargs)
                # Use object.__setattr__ for custom fields
                object.__setattr__(self, 'test_param', test_param)
            
            async def _run_async_impl(self, ctx):
                yield Event(type="test", data=self.test_param)
        
        self.factory.register_custom_agent("TestAgent", TestCustomAgent)
        
        spec_dict = {
            "api_version": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test-custom", "version": "1.0.0"},
            "spec": {
                "agent": {
                    "type": "custom",
                    "custom_class": "TestAgent",
                    "parameters": {"test_param": "test_value"}
                }
            }
        }
        
        agent = self.factory.build_agent_from_dict(spec_dict)
        
        assert isinstance(agent, TestCustomAgent)
        assert agent.name == "test_custom"  # Name should have hyphens replaced with underscores
        assert agent.test_param == "test_value"
    
    def test_build_custom_agent_missing_class(self):
        """Test building fails when custom_class is missing."""
        spec_dict = {
            "api_version": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test-custom", "version": "1.0.0"},
            "spec": {
                "agent": {
                    "type": "custom"
                    # Missing custom_class
                }
            }
        }
        
        with pytest.raises(SpecificationError, match="needs 'custom_class' field"):
            self.factory.build_agent_from_dict(spec_dict)
    
    def test_build_custom_agent_unregistered_class(self):
        """Test building fails when custom_class is not registered."""
        spec_dict = {
            "api_version": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test-custom", "version": "1.0.0"},
            "spec": {
                "agent": {
                    "type": "custom",
                    "custom_class": "UnregisteredAgent"
                }
            }
        }
        
        with pytest.raises(SpecificationError, match="not registered"):
            self.factory.build_agent_from_dict(spec_dict)
    
    def test_build_custom_agent_with_sub_agents(self):
        """Test custom agent building with sub-agents."""
        class TestCustomAgent(BaseAgent):
            def __init__(self, name, sub_agents=None, **kwargs):
                super().__init__(name=name, sub_agents=sub_agents, **kwargs)
            
            async def _run_async_impl(self, ctx):
                yield Event(type="test", data=f"sub_agents: {len(self.sub_agents)}")
        
        self.factory.register_custom_agent("TestAgent", TestCustomAgent)
        
        # Create a real BaseAgent instance for sub-agent
        class MockSubAgent(BaseAgent):
            def __init__(self, name):
                super().__init__(name=name)
            
            async def _run_async_impl(self, ctx):
                yield Event(type="result", data=f"{self.name}_complete")
        
        # Mock sub-agent creation with real BaseAgent instance
        with patch.object(self.factory, '_build_sub_agents') as mock_build_sub:
            mock_sub_agent = MockSubAgent("sub_agent")
            mock_build_sub.return_value = [mock_sub_agent]
            
            spec_dict = {
                "api_version": "agent-engine/v1",
                "kind": "AgentSpec",
                "metadata": {"name": "test-custom", "version": "1.0.0"},
                "spec": {
                    "agent": {
                        "type": "custom",
                        "custom_class": "TestAgent"
                    },
                    "sub_agents": [{"spec_ref": "sub_agent"}]
                }
            }
            
            agent = self.factory.build_agent_from_dict(spec_dict)
            
            assert len(agent.sub_agents) == 1
            assert agent.sub_agents[0].name == "sub_agent"


class TestAdaptiveOrchestrator:
    """Test AdaptiveOrchestrator custom agent."""
    
    def setup_method(self):
        """Set up test agent."""
        # Create real BaseAgent instances instead of mocks
        class MockSubAgent(BaseAgent):
            def __init__(self, name):
                super().__init__(name=name)
                # Use object.__setattr__ for custom fields
                object.__setattr__(self, 'run_async', AsyncMock())
            
            async def _run_async_impl(self, ctx):
                yield Event(type="result", data=f"{self.name}_complete")
        
        self.mock_sub_agent1 = MockSubAgent("analyzer")
        self.mock_sub_agent2 = MockSubAgent("processor")
        
        self.agent = AdaptiveOrchestrator(
            name="test_orchestrator",
            sub_agents=[self.mock_sub_agent1, self.mock_sub_agent2],
            orchestration_pattern="adaptive",
            max_iterations=3
        )
    
    def test_initialization(self):
        """Test AdaptiveOrchestrator initialization."""
        assert self.agent.name == "test_orchestrator"
        assert len(self.agent.sub_agents) == 2
        assert self.agent.orchestration_pattern == "adaptive"
        assert self.agent.max_iterations == 3
        assert "analyzer" in self.agent.agents
        assert "processor" in self.agent.agents
    
    @pytest.mark.asyncio
    async def test_run_async_impl_adaptive_pattern(self):
        """Test adaptive orchestration pattern execution."""
        # Mock sub-agent responses
        self.mock_sub_agent1.run_async.return_value = iter([
            Event(type="result", data="analysis_complete")
        ])
        self.mock_sub_agent2.run_async.return_value = iter([
            Event(type="result", data="processing_complete")
        ])
        
        ctx = InvocationContext()
        events = []
        
        async for event in self.agent._run_async_impl(ctx):
            events.append(event)
        
        # Should execute analyzer first (iteration 0), then processor (iteration 1)
        assert len(events) >= 2  # At least result events + completion
        
        # Check completion event
        completion_events = [e for e in events if e.type == "completion"]
        assert len(completion_events) == 1
        completion_data = completion_events[0].data
        assert completion_data["orchestration_pattern"] == "adaptive"
        assert completion_data["iterations"] >= 1
    
    @pytest.mark.asyncio
    async def test_run_async_impl_max_iterations(self):
        """Test that orchestration respects max_iterations."""
        # Mock sub-agent that always returns results
        self.mock_sub_agent1.run_async.return_value = iter([
            Event(type="result", data="analysis_complete")
        ])
        
        ctx = InvocationContext()
        events = []
        
        async for event in self.agent._run_async_impl(ctx):
            events.append(event)
        
        completion_events = [e for e in events if e.type == "completion"]
        assert len(completion_events) == 1
        
        # Should not exceed max_iterations
        iterations = completion_events[0].data["iterations"]
        assert iterations <= self.agent.max_iterations
    
    def test_select_next_agent_adaptive(self):
        """Test agent selection logic for adaptive pattern."""
        # First iteration should select analyzer or first agent
        agent = self.agent._select_next_agent({}, 0)
        assert agent is not None
        assert agent.name in ["analyzer", "processor"]
        
        # Second iteration should select processor or next agent
        agent = self.agent._select_next_agent({}, 1)
        assert agent is not None
    
    def test_select_next_agent_sequential(self):
        """Test agent selection for sequential pattern."""
        sequential_agent = AdaptiveOrchestrator(
            name="sequential_test",
            sub_agents=[self.mock_sub_agent1, self.mock_sub_agent2],
            orchestration_pattern="sequential"
        )
        
        # Should select agents in order
        agent1 = sequential_agent._select_next_agent({}, 0)
        agent2 = sequential_agent._select_next_agent({}, 1)
        
        assert agent1 == self.mock_sub_agent1
        assert agent2 == self.mock_sub_agent2


class TestConditionalRouter:
    """Test ConditionalRouter custom agent."""
    
    def setup_method(self):
        """Set up test router."""
        # Create real BaseAgent instances instead of mocks
        class MockSubAgent(BaseAgent):
            def __init__(self, name):
                super().__init__(name=name)
                # Use object.__setattr__ for custom fields
                object.__setattr__(self, 'run_async', AsyncMock())
            
            async def _run_async_impl(self, ctx):
                yield Event(type="result", data=f"{self.name}_complete")
        
        self.mock_analyzer = MockSubAgent("analyzer")
        self.mock_demo = MockSubAgent("demo")
        
        self.routing_rules = {
            "input.type == 'analysis'": "analyzer",
            "input.priority > 5": "analyzer",
            "true": "demo"  # Default fallback
        }
        
        self.router = ConditionalRouter(
            name="test_router",
            sub_agents=[self.mock_analyzer, self.mock_demo],
            routing_rules=self.routing_rules
        )
    
    def test_initialization(self):
        """Test ConditionalRouter initialization."""
        assert self.router.name == "test_router"
        assert len(self.router.sub_agents) == 2
        assert self.router.routing_rules == self.routing_rules
        assert "analyzer" in self.router.agents
        assert "demo" in self.router.agents
    
    @pytest.mark.asyncio
    async def test_run_async_impl_condition_match(self):
        """Test routing when condition matches."""
        self.mock_analyzer.run_async.return_value = iter([
            Event(type="result", data="analysis_complete")
        ])
        
        ctx = InvocationContext(input={"type": "analysis"})
        events = []
        
        async for event in self.router._run_async_impl(ctx):
            events.append(event)
        
        # Should execute analyzer and provide routing summary
        routing_events = [e for e in events if e.type == "routing_complete"]
        assert len(routing_events) == 1
        
        routing_data = routing_events[0].data
        assert "analyzer" in routing_data["executed_agents"]
    
    @pytest.mark.asyncio
    async def test_run_async_impl_fallback(self):
        """Test routing fallback to default condition."""
        self.mock_demo.run_async.return_value = iter([
            Event(type="result", data="demo_complete")
        ])
        
        ctx = InvocationContext(input={"type": "other", "priority": 3})
        events = []
        
        async for event in self.router._run_async_impl(ctx):
            events.append(event)
        
        # Should execute demo (fallback) and provide routing summary
        routing_events = [e for e in events if e.type == "routing_complete"]
        assert len(routing_events) == 1
        
        routing_data = routing_events[0].data
        assert "demo" in routing_data["executed_agents"]
    
    def test_evaluate_condition_simple(self):
        """Test simple condition evaluation."""
        assert self.router._evaluate_condition("true", {}) == True
        assert self.router._evaluate_condition("false", {}) == False
    
    def test_evaluate_condition_input_property(self):
        """Test input property condition evaluation."""
        data = {"type": "analysis", "priority": 7}
        
        # These should work with basic property checks
        assert self.router._evaluate_condition("input.type", data) == True
        assert self.router._evaluate_condition("input.priority", data) == True
    
    def test_evaluate_condition_complex(self):
        """Test complex condition evaluation with eval."""
        data = {"type": "analysis", "priority": 7}
        
        # These use safe eval
        assert self.router._evaluate_condition("input['type'] == 'analysis'", data) == True
        assert self.router._evaluate_condition("input['priority'] > 5", data) == True
        assert self.router._evaluate_condition("input['priority'] < 5", data) == False
    
    def test_evaluate_condition_error_handling(self):
        """Test condition evaluation error handling."""
        # Invalid conditions should return False
        assert self.router._evaluate_condition("invalid.syntax..error", {}) == False
        assert self.router._evaluate_condition("undefined_var", {}) == False


class TestStatefulWorkflow:
    """Test StatefulWorkflow custom agent."""
    
    def setup_method(self):
        """Set up test workflow."""
        # Create real BaseAgent instances instead of mocks
        class MockSubAgent(BaseAgent):
            def __init__(self, name):
                super().__init__(name=name)
                # Use object.__setattr__ for custom fields
                object.__setattr__(self, 'run_async', AsyncMock())
            
            async def _run_async_impl(self, ctx):
                yield Event(type="result", data=f"{self.name}_complete")
        
        self.mock_step1 = MockSubAgent("step1")
        self.mock_step2 = MockSubAgent("step2")
        
        self.workflow = StatefulWorkflow(
            name="test_workflow",
            sub_agents=[self.mock_step1, self.mock_step2],
            workflow_steps=["step1", "step2"],
            allow_restart=True
        )
    
    def test_initialization(self):
        """Test StatefulWorkflow initialization."""
        assert self.workflow.name == "test_workflow"
        assert self.workflow.workflow_steps == ["step1", "step2"]
        assert self.workflow.allow_restart == True
        assert len(self.workflow.agents) == 2
    
    @pytest.mark.asyncio
    async def test_run_async_impl_success(self):
        """Test successful workflow execution."""
        self.mock_step1.run_async.return_value = iter([
            Event(type="result", data="step1_complete")
        ])
        self.mock_step2.run_async.return_value = iter([
            Event(type="result", data="step2_complete")
        ])
        
        ctx = InvocationContext()
        events = []
        
        async for event in self.workflow._run_async_impl(ctx):
            events.append(event)
        
        # Should have step completion events and final workflow event
        step_events = [e for e in events if e.type == "step_completed"]
        assert len(step_events) == 2
        
        workflow_events = [e for e in events if e.type == "workflow_complete"]
        assert len(workflow_events) == 1
        
        workflow_data = workflow_events[0].data
        assert workflow_data["success"] == True
        assert len(workflow_data["completed_steps"]) == 2
        assert len(workflow_data["failed_steps"]) == 0
    
    @pytest.mark.asyncio
    async def test_run_async_impl_failure(self):
        """Test workflow execution with failure."""
        self.mock_step1.run_async.return_value = iter([
            Event(type="result", data="step1_complete")
        ])
        self.mock_step2.run_async.return_value = iter([
            Event(type="error", data="step2_failed")
        ])
        
        ctx = InvocationContext()
        events = []
        
        async for event in self.workflow._run_async_impl(ctx):
            events.append(event)
        
        # Should have failure events
        step_failed_events = [e for e in events if e.type == "step_failed"]
        assert len(step_failed_events) == 1
        
        workflow_events = [e for e in events if e.type == "workflow_failed"]
        assert len(workflow_events) == 1
        
        workflow_data = workflow_events[0].data
        assert workflow_data["success"] == False
        assert len(workflow_data["completed_steps"]) == 1
        assert len(workflow_data["failed_steps"]) == 1


class TestCustomAgentsIntegration:
    """Test integration of custom agents with the factory."""
    
    def test_built_in_agents_registry(self):
        """Test built-in custom agents registry."""
        expected_agents = ["AdaptiveOrchestrator", "ConditionalRouter", "StatefulWorkflow"]
        
        for agent_name in expected_agents:
            assert agent_name in BUILT_IN_CUSTOM_AGENTS
            agent_class = BUILT_IN_CUSTOM_AGENTS[agent_name]
            assert issubclass(agent_class, BaseAgent)
            assert hasattr(agent_class, '_run_async_impl')
    
    def test_register_built_in_agents(self):
        """Test registration of built-in agents."""
        factory = UniversalAgentFactory()
        
        # Clear registry first
        factory.custom_registry.clear()
        
        # Register built-in agents
        register_built_in_agents(factory)
        
        # Check that all built-in agents are registered
        expected_agents = ["AdaptiveOrchestrator", "ConditionalRouter", "StatefulWorkflow"]
        for agent_name in expected_agents:
            assert agent_name in factory.custom_registry
    
    def test_factory_supports_custom_type(self):
        """Test that factory supports 'custom' agent type."""
        factory = UniversalAgentFactory()
        supported_types = factory.list_supported_types()
        assert "custom" in supported_types
    
    def test_custom_agent_specification_loading(self):
        """Test loading custom agent from specification file."""
        factory = UniversalAgentFactory()
        
        # Create a temporary specification file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            spec_data = {
                "api_version": "agent-engine/v1",
                "kind": "AgentSpec",
                "metadata": {"name": "test-adaptive", "version": "1.0.0"},
                "spec": {
                    "agent": {
                        "type": "custom",
                        "custom_class": "AdaptiveOrchestrator",
                        "parameters": {
                            "orchestration_pattern": "adaptive",
                            "max_iterations": 5
                        }
                    }
                }
            }
            yaml.dump(spec_data, f)
            spec_file = f.name
        
        try:
            # Load and build agent from file
            with open(spec_file) as f:
                spec_dict = yaml.safe_load(f)
            
            agent = factory.build_agent_from_dict(spec_dict)
            
            assert isinstance(agent, AdaptiveOrchestrator)
            assert agent.name == "test_adaptive"
            assert agent.orchestration_pattern == "adaptive"
            assert agent.max_iterations == 5
            
        finally:
            # Clean up
            Path(spec_file).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])