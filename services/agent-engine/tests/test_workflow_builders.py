"""
Unit tests for workflow agent builders

Tests all workflow builders with comprehensive coverage:
- SequentialAgentBuilder
- ParallelAgentBuilder  
- LoopAgentBuilder
- WorkflowBuilderBase
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.core.builders.workflow_builders import (
    SequentialAgentBuilder, 
    ParallelAgentBuilder, 
    LoopAgentBuilder,
    WorkflowBuilderBase,
    SpecificationError
)
from src.core.composition import AgentSpec, AgentContext


class TestWorkflowBuilderBase:
    """Test base workflow builder functionality"""
    
    def setup_method(self):
        """Create a concrete test builder"""
        class TestableWorkflowBuilder(WorkflowBuilderBase):
            def can_build(self, agent_type: str) -> bool:
                return agent_type == "test"
            def validate_spec(self, spec) -> bool:
                return True
            def build(self, spec, context):
                return Mock()
        self.TestableWorkflowBuilder = TestableWorkflowBuilder
    
    def test_init_with_factory(self):
        """Test initialization with factory"""
        mock_factory = Mock()
        builder = self.TestableWorkflowBuilder(factory=mock_factory)
        
        assert builder.factory == mock_factory
    
    def test_init_without_factory(self):
        """Test initialization without factory"""
        builder = self.TestableWorkflowBuilder()
        
        assert builder.factory is None
    
    def test_build_sub_agents_with_factory(self):
        """Test building sub-agents using factory"""
        mock_factory = Mock()
        mock_agent1 = Mock()
        mock_agent2 = Mock()
        mock_factory.build_agent.side_effect = [mock_agent1, mock_agent2]
        
        builder = self.TestableWorkflowBuilder(factory=mock_factory)
        context = AgentContext(
            user_id="test_user",
            session_id="test_session",
            environment="test",
            variables={"base_var": "value"}
        )
        
        sub_agent_specs = [
            {"spec_ref": "agent1", "variables": {"var1": "value1"}},
            {"spec_ref": "agent2", "variables": {"var2": "value2"}}
        ]
        
        sub_agents = builder.build_sub_agents(sub_agent_specs, context)
        
        assert len(sub_agents) == 2
        assert sub_agents[0] == mock_agent1
        assert sub_agents[1] == mock_agent2
        assert mock_factory.build_agent.call_count == 2
    
    def test_build_sub_agents_without_factory(self):
        """Test building sub-agents without factory raises error"""
        builder = self.TestableWorkflowBuilder()
        context = AgentContext()
        sub_agent_specs = [{"spec_ref": "agent1"}]
        
        with pytest.raises(SpecificationError, match="Factory not provided"):
            builder.build_sub_agents(sub_agent_specs, context)
    
    def test_build_sub_agents_invalid_spec(self):
        """Test building sub-agents with invalid spec"""
        mock_factory = Mock()
        builder = self.TestableWorkflowBuilder(factory=mock_factory)
        context = AgentContext()
        
        # Spec without spec_ref
        sub_agent_specs = [{"name": "agent1"}]  # Missing spec_ref
        
        sub_agents = builder.build_sub_agents(sub_agent_specs, context)
        
        assert len(sub_agents) == 0
        assert mock_factory.build_agent.call_count == 0
    
    def test_enhance_context(self):
        """Test context enhancement with sub-agent variables"""
        builder = self.TestableWorkflowBuilder()
        parent_context = AgentContext(
            user_id="user123",
            session_id="session123",
            environment="test",
            variables={"parent_var": "parent_value"}
        )
        spec = {
            "name": "sub_agent",
            "variables": {"sub_var": "sub_value"}
        }
        
        enhanced_context = builder._enhance_context(parent_context, spec)
        
        assert enhanced_context.user_id == "user123"
        assert enhanced_context.session_id == "session123"
        assert enhanced_context.environment == "test"
        assert enhanced_context.variables["parent_var"] == "parent_value"
        assert enhanced_context.variables["sub_var"] == "sub_value"
        assert enhanced_context.parent_agent == "sub_agent"
    
    def test_validate_workflow_spec_valid(self):
        """Test validation of valid workflow spec"""
        builder = self.TestableWorkflowBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": [
                    {"spec_ref": "agent1"},
                    {"spec_ref": "agent2"}
                ]
            }
        )
        
        assert builder.validate_workflow_spec(spec) == True
    
    def test_validate_workflow_spec_no_sub_agents(self):
        """Test validation fails without sub-agents"""
        builder = self.TestableWorkflowBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={"agent": {"type": "sequential"}}
        )
        
        assert builder.validate_workflow_spec(spec) == False
    
    def test_validate_workflow_spec_empty_sub_agents(self):
        """Test validation fails with empty sub-agents"""
        builder = self.TestableWorkflowBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": []
            }
        )
        
        assert builder.validate_workflow_spec(spec) == False
    
    def test_validate_workflow_spec_invalid_sub_agent(self):
        """Test validation fails with invalid sub-agent spec"""
        builder = self.TestableWorkflowBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": [
                    {"name": "agent1"}  # Missing spec_ref
                ]
            }
        )
        
        assert builder.validate_workflow_spec(spec) == False


class TestSequentialAgentBuilder:
    """Test sequential agent builder"""
    
    def test_can_build_sequential(self):
        """Test builder recognizes sequential type"""
        builder = SequentialAgentBuilder()
        assert builder.can_build("sequential") == True
        assert builder.can_build("parallel") == False
        assert builder.can_build("loop") == False
        assert builder.can_build("llm") == False
    
    def test_validate_spec_valid(self):
        """Test validation of valid sequential spec"""
        builder = SequentialAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": [
                    {"spec_ref": "agent1"},
                    {"spec_ref": "agent2"}
                ]
            }
        )
        
        assert builder.validate_spec(spec) == True
    
    def test_validate_spec_wrong_type(self):
        """Test validation fails with wrong agent type"""
        builder = SequentialAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "parallel"},  # Wrong type
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        
        assert builder.validate_spec(spec) == False
    
    @patch('src.core.builders.workflow_builders.SequentialAgent')
    def test_build_sequential_agent(self, mock_sequential):
        """Test building sequential agent with factory"""
        mock_factory = Mock()
        mock_sub_agent1 = Mock()
        mock_sub_agent2 = Mock()
        mock_factory.build_agent.side_effect = [mock_sub_agent1, mock_sub_agent2]
        
        builder = SequentialAgentBuilder(factory=mock_factory)
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_sequential", "version": "1.0.0", "description": "Test sequential agent"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": [
                    {"spec_ref": "agent1"},
                    {"spec_ref": "agent2"}
                ]
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_sequential.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        mock_sequential.assert_called_once()
        call_args = mock_sequential.call_args
        assert call_args.kwargs['name'] == "test_sequential"
        assert call_args.kwargs['description'] == "Test sequential agent"
        assert len(call_args.kwargs['sub_agents']) == 2
        assert agent == mock_agent_instance
    
    def test_build_invalid_spec(self):
        """Test building with invalid spec raises error"""
        mock_factory = Mock()
        builder = SequentialAgentBuilder(factory=mock_factory)
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={"agent": {"type": "parallel"}}  # Wrong type
        )
        context = AgentContext()
        
        with pytest.raises(SpecificationError):
            builder.build(spec, context)
    
    def test_build_no_sub_agents(self):
        """Test building with no sub-agents raises error"""
        mock_factory = Mock()
        mock_factory.build_agent.return_value = []  # No sub-agents built
        
        builder = SequentialAgentBuilder(factory=mock_factory)
        builder.build_sub_agents = Mock(return_value=[])  # Override to return empty
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "sequential"},
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        context = AgentContext()
        
        with pytest.raises(SpecificationError, match="at least one sub-agent"):
            builder.build(spec, context)


class TestParallelAgentBuilder:
    """Test parallel agent builder"""
    
    def test_can_build_parallel(self):
        """Test builder recognizes parallel type"""
        builder = ParallelAgentBuilder()
        assert builder.can_build("parallel") == True
        assert builder.can_build("sequential") == False
        assert builder.can_build("loop") == False
    
    def test_validate_spec_valid(self):
        """Test validation of valid parallel spec"""
        builder = ParallelAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {"type": "parallel"},
                "sub_agents": [
                    {"spec_ref": "agent1"},
                    {"spec_ref": "agent2"}
                ]
            }
        )
        
        assert builder.validate_spec(spec) == True
    
    @patch('src.core.builders.workflow_builders.ParallelAgent')
    def test_build_parallel_agent(self, mock_parallel):
        """Test building parallel agent with factory"""
        mock_factory = Mock()
        mock_sub_agent1 = Mock()
        mock_sub_agent2 = Mock()
        mock_factory.build_agent.side_effect = [mock_sub_agent1, mock_sub_agent2]
        
        builder = ParallelAgentBuilder(factory=mock_factory)
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_parallel", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "parallel",
                    "parameters": {"concurrency": 2}  # ADK parameters
                },
                "sub_agents": [
                    {"spec_ref": "agent1"},
                    {"spec_ref": "agent2"}
                ]
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_parallel.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        mock_parallel.assert_called_once()
        call_args = mock_parallel.call_args
        assert call_args.kwargs['name'] == "test_parallel"
        assert len(call_args.kwargs['sub_agents']) == 2
        assert 'concurrency' in call_args.kwargs  # Parameters passed through
        assert agent == mock_agent_instance


class TestLoopAgentBuilder:
    """Test loop agent builder"""
    
    def test_can_build_loop(self):
        """Test builder recognizes loop type"""
        builder = LoopAgentBuilder()
        assert builder.can_build("loop") == True
        assert builder.can_build("sequential") == False
        assert builder.can_build("parallel") == False
    
    def test_validate_spec_valid(self):
        """Test validation of valid loop spec"""
        builder = LoopAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "loop",
                    "loop_config": {"max_iterations": 5}
                },
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        
        assert builder.validate_spec(spec) == True
    
    def test_validate_spec_no_max_iterations(self):
        """Test validation with warning for missing max_iterations"""
        builder = LoopAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "loop",
                    "loop_config": {}  # No max_iterations
                },
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        
        # Should still validate but warn
        assert builder.validate_spec(spec) == True
    
    @patch('src.core.builders.workflow_builders.LoopAgent')
    def test_build_loop_agent(self, mock_loop):
        """Test building loop agent with correct parameters"""
        mock_factory = Mock()
        mock_sub_agent = Mock()
        mock_factory.build_agent.return_value = mock_sub_agent
        
        builder = LoopAgentBuilder(factory=mock_factory)
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_loop", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "loop",
                    "loop_config": {
                        "max_iterations": 10
                    }
                },
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_loop.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        mock_loop.assert_called_once()
        call_args = mock_loop.call_args
        assert call_args.kwargs['name'] == "test_loop"
        assert call_args.kwargs['max_iterations'] == 10
        assert len(call_args.kwargs['sub_agents']) == 1
        assert agent == mock_agent_instance
    
    @patch('src.core.builders.workflow_builders.LoopAgent')
    def test_build_loop_agent_default_iterations(self, mock_loop):
        """Test building loop agent with default max_iterations"""
        mock_factory = Mock()
        mock_sub_agent = Mock()
        mock_factory.build_agent.return_value = mock_sub_agent
        
        builder = LoopAgentBuilder(factory=mock_factory)
        
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_loop", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "loop",
                    "loop_config": {}  # No max_iterations specified
                },
                "sub_agents": [{"spec_ref": "agent1"}]
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_loop.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        mock_loop.assert_called_once()
        call_args = mock_loop.call_args
        assert call_args.kwargs['max_iterations'] == 10  # Default value