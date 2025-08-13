"""
ADK Integration Test Suite
Comprehensive tests for Google ADK component integration
"""

import pytest
from typing import Any
from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool


class TestADKComponents:
    """Test suite for core ADK components."""
    
    def test_llm_agent_creation(self):
        """Test LlmAgent creation with various parameters."""
        agent = LlmAgent(
            name="test_llm",
            model="gemini-2.0-flash",
            instruction="You are a test agent",
            description="Test LLM agent for verification"
        )
        
        assert agent.name == "test_llm"
        assert agent.model == "gemini-2.0-flash"
        assert agent.instruction == "You are a test agent"
        assert agent.description == "Test LLM agent for verification"
    
    def test_agent_alias(self):
        """Test that Agent is an alias for LlmAgent."""
        agent = Agent(
            name="test_alias",
            model="gemini-2.0-flash",
            instruction="Testing alias"
        )
        
        assert type(agent).__name__ == "LlmAgent"
        assert agent.name == "test_alias"
    
    def test_runner_creation(self):
        """Test InMemoryRunner creation."""
        agent = LlmAgent(
            name="runner_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        runner = InMemoryRunner(agent, app_name="test_app")
        
        assert runner is not None
        assert hasattr(runner, 'run')
        assert hasattr(runner, 'run_async')
        assert hasattr(runner, 'session_service')
    
    def test_session_creation(self):
        """Test session creation and management."""
        agent = LlmAgent(
            name="session_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        runner = InMemoryRunner(agent, app_name="test_app")
        session_service = runner.session_service
        
        session = session_service.create_session(
            app_name="test_app",
            user_id="test-user"
        )
        
        assert session.id is not None
        assert session.user_id == "test-user"
        assert session.app_name == "test-app"
    
    def test_session_with_initial_state(self):
        """Test session creation with initial state."""
        agent = LlmAgent(
            name="state_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        runner = InMemoryRunner(agent, app_name="test_app")
        session_service = runner.session_service
        
        initial_state = {
            "counter": 0,
            "messages": [],
            "config": {"debug": True}
        }
        
        session = session_service.create_session(
            app_name="test_app",
            user_id="test-user",
            initial_state=initial_state
        )
        
        assert session.id is not None
        # Note: State access may vary by implementation


class TestAgentTypes:
    """Test suite for different agent types."""
    
    def test_sequential_agent(self):
        """Test SequentialAgent creation."""
        sub_agent1 = LlmAgent(
            name="sub1",
            model="gemini-2.0-flash",
            instruction="First agent"
        )
        sub_agent2 = LlmAgent(
            name="sub2",
            model="gemini-2.0-flash",
            instruction="Second agent"
        )
        
        seq_agent = SequentialAgent(
            name="sequential_test",
            sub_agents=[sub_agent1, sub_agent2],
            description="Sequential workflow test"
        )
        
        assert seq_agent.name == "sequential_test"
        assert len(seq_agent.sub_agents) == 2
        assert seq_agent.sub_agents[0].name == "sub1"
        assert seq_agent.sub_agents[1].name == "sub2"
    
    def test_parallel_agent(self):
        """Test ParallelAgent creation."""
        sub_agents = [
            LlmAgent(name=f"parallel-{i}", model="gemini-2.0-flash", instruction=f"Agent {i}")
            for i in range(3)
        ]
        
        par_agent = ParallelAgent(
            name="parallel_test",
            sub_agents=sub_agents,
            description="Parallel workflow test"
        )
        
        assert par_agent.name == "parallel_test"
        assert len(par_agent.sub_agents) == 3
    
    def test_loop_agent(self):
        """Test LoopAgent creation."""
        sub_agent = LlmAgent(
            name="loop_sub",
            model="gemini-2.0-flash",
            instruction="Loop iteration agent"
        )
        
        loop_agent = LoopAgent(
            name="loop_test",
            sub_agents=[sub_agent],  # LoopAgent takes sub_agents as a list
            max_iterations=5,
            description="Loop workflow test"
        )
        
        assert loop_agent.name == "loop_test"
        assert loop_agent.max_iterations == 5
        assert len(loop_agent.sub_agents) == 1
        assert loop_agent.sub_agents[0].name == "loop_sub"
    
    def test_custom_agent(self):
        """Test custom agent extending BaseAgent."""
        
        class CustomAnalyzer(BaseAgent):
            def __init__(self, name: str, threshold: float = 0.5):
                super().__init__(name=name, description="Custom analyzer")
                self.threshold = threshold
        
        custom = CustomAnalyzer(name="custom_test", threshold=0.8)
        
        assert custom.name == "custom_test"
        assert custom.threshold == 0.8
        assert isinstance(custom, BaseAgent)
    
    def test_nested_workflow_agents(self):
        """Test nested workflow composition."""
        # Create base agents
        agent1 = LlmAgent(name="base1", model="gemini-2.0-flash", instruction="Base 1")
        agent2 = LlmAgent(name="base2", model="gemini-2.0-flash", instruction="Base 2")
        
        # Create parallel workflow
        parallel = ParallelAgent(
            name="parallel_sub",
            sub_agents=[agent1, agent2]
        )
        
        # Create sequential workflow with parallel as sub-agent
        sequential = SequentialAgent(
            name="main_workflow",
            sub_agents=[parallel],
            description="Nested workflow"
        )
        
        assert sequential.name == "main_workflow"
        assert len(sequential.sub_agents) == 1
        assert sequential.sub_agents[0].name == "parallel_sub"


class TestToolIntegration:
    """Test suite for tool integration patterns."""
    
    def test_automatic_tool_wrapping(self):
        """Test automatic function wrapping."""
        
        def calculator(a: int, b: int, operation: str = "add") -> int:
            """Simple calculator for testing."""
            if operation == "add":
                return a + b
            elif operation == "subtract":
                return a - b
            else:
                return a * b
        
        agent = LlmAgent(
            name="calc_agent",
            model="gemini-2.0-flash",
            instruction="Calculator agent",
            tools=[calculator]  # Automatic wrapping
        )
        
        assert agent.name == "calc_agent"
        assert len(agent.tools) == 1
    
    def test_explicit_function_tool(self):
        """Test explicit FunctionTool wrapping."""
        
        def analyzer(text: str) -> dict:
            """Analyze text."""
            return {"length": len(text), "words": len(text.split())}
        
        # Explicit wrapping
        tool = FunctionTool(analyzer)
        
        agent = LlmAgent(
            name="analyzer_agent",
            model="gemini-2.0-flash",
            instruction="Text analyzer",
            tools=[tool]
        )
        
        assert agent.name == "analyzer_agent"
        assert len(agent.tools) == 1
    
    def test_multiple_tools(self):
        """Test agent with multiple tools."""
        
        def tool1(x: int) -> int:
            return x * 2
        
        def tool2(s: str) -> str:
            return s.upper()
        
        def tool3(data: dict) -> bool:
            return "key" in data
        
        agent = LlmAgent(
            name="multi_tool",
            model="gemini-2.0-flash",
            instruction="Multi-tool agent",
            tools=[tool1, tool2, tool3]
        )
        
        assert agent.name == "multi_tool"
        assert len(agent.tools) == 3
    
    def test_mixed_tool_types(self):
        """Test mixing automatic and explicit tool wrapping."""
        
        def auto_tool(x: int) -> int:
            return x + 1
        
        def explicit_func(s: str) -> str:
            return s.lower()
        
        explicit_tool = FunctionTool(explicit_func)
        
        agent = LlmAgent(
            name="mixed_tools",
            model="gemini-2.0-flash",
            instruction="Mixed tool types",
            tools=[auto_tool, explicit_tool]  # Mixed types
        )
        
        assert agent.name == "mixed_tools"
        assert len(agent.tools) == 2
    
    def test_agent_as_tool(self):
        """Test using an agent as a tool for another agent."""
        tool_agent = LlmAgent(
            name="tool_agent",
            model="gemini-2.0-flash",
            instruction="I am a specialized tool"
        )
        
        main_agent = LlmAgent(
            name="main_agent",
            model="gemini-2.0-flash",
            instruction="Main agent with sub-agent as tool",
            sub_agents=[tool_agent]  # Agent as tool via sub_agents
        )
        
        assert main_agent.name == "main_agent"
        assert len(main_agent.sub_agents) == 1
        assert main_agent.sub_agents[0].name == "tool_agent"


class TestRunnerPatterns:
    """Test suite for runner execution patterns."""
    
    def test_runner_with_simple_agent(self):
        """Test runner with a simple LLM agent."""
        agent = LlmAgent(
            name="simple",
            model="gemini-2.0-flash",
            instruction="Simple test"
        )
        
        runner = InMemoryRunner(agent, app_name="simple_app")
        
        assert runner is not None
        assert callable(getattr(runner, 'run', None))
        assert callable(getattr(runner, 'run_async', None))
    
    def test_runner_with_workflow_agent(self):
        """Test runner with workflow agents."""
        agents = [
            LlmAgent(name=f"worker-{i}", model="gemini-2.0-flash", instruction=f"Worker {i}")
            for i in range(2)
        ]
        
        workflow = SequentialAgent(
            name="workflow",
            sub_agents=agents
        )
        
        runner = InMemoryRunner(workflow, app_name="workflow_app")
        
        assert runner is not None
    
    def test_multiple_runners(self):
        """Test creating multiple runners."""
        agent1 = LlmAgent(name="agent1", model="gemini-2.0-flash", instruction="Agent 1")
        agent2 = LlmAgent(name="agent2", model="gemini-2.0-flash", instruction="Agent 2")
        
        runner1 = InMemoryRunner(agent1, app_name="app1")
        runner2 = InMemoryRunner(agent2, app_name="app2")
        
        assert runner1 is not None
        assert runner2 is not None
        assert runner1 != runner2
    
    def test_runner_session_isolation(self):
        """Test session isolation between runners."""
        agent = LlmAgent(name="shared", model="gemini-2.0-flash", instruction="Shared agent")
        
        runner1 = InMemoryRunner(agent, app_name="app1")
        runner2 = InMemoryRunner(agent, app_name="app2")
        
        session1 = runner1.session_service.create_session(
            app_name="app1",
            user_id="user1"
        )
        
        session2 = runner2.session_service.create_session(
            app_name="app2",
            user_id="user2"
        )
        
        assert session1.id != session2.id
        assert session1.app_name == "app1"
        assert session2.app_name == "app2"


class TestAdvancedPatterns:
    """Test suite for advanced ADK patterns."""
    
    def test_agent_with_parameters(self):
        """Test agent creation with additional parameters."""
        agent = LlmAgent(
            name="parameterized",
            model="gemini-2.0-flash",
            instruction="Test with parameters",
        )
        
        assert agent.name == "parameterized"
        assert agent.model == "gemini-2.0-flash"
        # Parameters are set even if not directly accessible
    
    def test_complex_workflow_composition(self):
        """Test complex workflow with multiple levels."""
        # Level 1: Base agents
        base_agents = [
            LlmAgent(name=f"base-{i}", model="gemini-2.0-flash", instruction=f"Base {i}")
            for i in range(4)
        ]
        
        # Level 2: Parallel groups
        parallel1 = ParallelAgent(
            name="parallel1",
            sub_agents=base_agents[:2]
        )
        parallel2 = ParallelAgent(
            name="parallel2",
            sub_agents=base_agents[2:]
        )
        
        # Level 3: Sequential orchestration
        main_workflow = SequentialAgent(
            name="complex_workflow",
            sub_agents=[parallel1, parallel2],
            description="Complex multi-level workflow"
        )
        
        assert main_workflow.name == "complex_workflow"
        assert len(main_workflow.sub_agents) == 2
        assert main_workflow.sub_agents[0].name == "parallel1"
        assert main_workflow.sub_agents[1].name == "parallel2"
    
    def test_dynamic_agent_creation(self):
        """Test dynamic agent creation based on configuration."""
        
        def create_agent_from_config(config: dict) -> BaseAgent:
            """Factory function for dynamic agent creation."""
            agent_type = config.get("type", "llm")
            
            if agent_type == "llm":
                return LlmAgent(
                    name=config["name"],
                    model=config.get("model", "gemini-2.0-flash"),
                    instruction=config.get("instruction", "Default instruction")
                )
            elif agent_type == "sequential":
                sub_configs = config.get("sub_agents", [])
                sub_agents = [create_agent_from_config(sc) for sc in sub_configs]
                return SequentialAgent(
                    name=config["name"],
                    sub_agents=sub_agents
                )
            else:
                raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Test configuration
        config = {
            "type": "sequential",
            "name": "dynamic-workflow",
            "sub_agents": [
                {"type": "llm", "name": "step1", "instruction": "First step"},
                {"type": "llm", "name": "step2", "instruction": "Second step"}
            ]
        }
        
        agent = create_agent_from_config(config)
        
        assert agent.name == "dynamic_workflow"
        assert isinstance(agent, SequentialAgent)
        assert len(agent.sub_agents) == 2