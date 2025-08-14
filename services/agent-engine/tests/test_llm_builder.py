import pytest
from unittest.mock import Mock, patch, MagicMock
from google.adk.agents import LlmAgent

from src.core.builders.llm_builder import (
    LlmAgentBuilder, ToolLoader
)
from src.core.composition import AgentSpec, AgentContext

class TestLlmAgentBuilder:
    def test_builder_initialization(self):
        """Test LLM agent builder initializes correctly"""
        builder = LlmAgentBuilder()
        assert builder.tool_loader is not None
        assert builder.sub_agent_factory is None
    
    def test_can_build_llm_type(self):
        """Test builder recognizes LLM agent types"""
        builder = LlmAgentBuilder()
        assert builder.can_build("llm") == True
        assert builder.can_build("agent") == True
        assert builder.can_build("sequential") == False
    
    def test_build_instruction(self):
        """Test instruction building with variable substitution"""
        builder = LlmAgentBuilder()
        context = AgentContext(variables={"role": "analyst", "domain": "finance"})
        
        template = "You are a ${role} specializing in ${domain}."
        instruction = builder._build_instruction(template, context)
        assert instruction == "You are a analyst specializing in finance."
    
    def test_missing_variable_placeholder(self):
        """Test missing variables get placeholders"""
        builder = LlmAgentBuilder()
        context = AgentContext(variables={"role": "analyst"})
        
        template = "You are a ${role} in ${domain}."
        instruction = builder._build_instruction(template, context)
        assert instruction == "You are a analyst in [domain]."
    
    def test_empty_template_error(self):
        """Test error on empty template"""
        builder = LlmAgentBuilder()
        context = AgentContext()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            builder._build_instruction("", context)
    
    def test_validate_spec_valid(self):
        """Test validation of valid specification"""
        builder = LlmAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "llm",
                    "instruction_template": "You are a helper.",
                    "model": {"primary": "gemini-2.0-flash"}
                }
            }
        )
        
        assert builder.validate_spec(spec) == True
    
    def test_validate_spec_missing_instruction(self):
        """Test validation fails without instruction template"""
        builder = LlmAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"}
                }
            }
        )
        
        assert builder.validate_spec(spec) == False
    
    @patch('src.core.builders.llm_builder.LlmAgent')
    def test_build_simple_agent(self, mock_llm_agent):
        """Test building simple LLM agent"""
        builder = LlmAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_agent", "version": "1.0.0", "description": "Test agent"},
            spec={
                "agent": {
                    "type": "llm",
                    "instruction_template": "You are a helpful assistant.",
                    "model": {"primary": "gemini-2.0-flash"},
                    "parameters": {"temperature": 0.2}
                }
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_llm_agent.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        mock_llm_agent.assert_called_once()
        call_args = mock_llm_agent.call_args
        assert call_args.kwargs['name'] == "test_agent"
        assert call_args.kwargs['instruction'] == "You are a helpful assistant."
        assert call_args.kwargs['temperature'] == 0.2
    
    @patch('src.core.builders.llm_builder.LlmAgent')
    def test_build_agent_with_fallbacks(self, mock_llm_agent):
        """Test building agent with fallback models"""
        builder = LlmAgentBuilder()
        spec = AgentSpec(
            api_version="agent-engine/v1",
            kind="AgentSpec",
            metadata={"name": "test_agent", "version": "1.0.0"},
            spec={
                "agent": {
                    "type": "llm",
                    "instruction_template": "Test instruction",
                    "model": {
                        "primary": "gemini-2.0-flash",
                        "fallbacks": ["gemini-2.5-pro", "gemini-2.5-flash"]
                    }
                }
            }
        )
        context = AgentContext()
        
        mock_agent_instance = Mock()
        mock_llm_agent.return_value = mock_agent_instance
        
        agent = builder.build(spec, context)
        
        call_args = mock_llm_agent.call_args
        assert call_args.kwargs['model'] == "gemini-2.0-flash"
        assert call_args.kwargs.get('fallback_models') == ["gemini-2.5-pro", "gemini-2.5-flash"]
    
    def test_evaluate_condition(self):
        """Test safe condition evaluation"""
        builder = LlmAgentBuilder()
        context = AgentContext(variables={"requires_analysis": True, "skip_validation": False})
        
        assert builder._evaluate_condition("true", context) == True
        assert builder._evaluate_condition("false", context) == False
        assert builder._evaluate_condition("input.requires_analysis", context) == True
        assert builder._evaluate_condition("input.skip_validation", context) == False
        assert builder._evaluate_condition("requires_analysis", context) == True
        assert builder._evaluate_condition("invalid_condition!", context) == False

class TestToolLoader:
    def test_loader_initialization(self):
        """Test tool loader initializes correctly"""
        loader = ToolLoader()
        assert loader.tool_registry is None
        assert isinstance(loader.built_in_tools, dict)
    
    def test_load_inline_tool(self):
        """Test loading inline tool definition"""
        loader = ToolLoader()
        spec = {
            "name": "test_tool",
            "source": "inline",
            "definition": "def test_tool(x): return x * 2"
        }
        
        tool = loader._load_single_tool(spec)
        assert tool is not None
        assert callable(tool)
        assert tool(5) == 10
    
    def test_load_from_registry(self):
        """Test loading tool from registry"""
        mock_registry = Mock()
        mock_tool = Mock()
        mock_registry.get_tool.return_value = mock_tool
        
        loader = ToolLoader(tool_registry=mock_registry)
        spec = {"name": "registered_tool", "source": "registry"}
        
        tool = loader._load_single_tool(spec)
        assert tool == mock_tool
        mock_registry.get_tool.assert_called_once_with("registered_tool")
    
    @patch('src.core.builders.llm_builder.google_search')
    def test_load_google_search(self, mock_google_search):
        """Test loading google_search built-in tool"""
        loader = ToolLoader()
        spec = {"name": "google_search", "source": "builtin"}
        
        tool = loader._load_single_tool(spec)
        assert tool == mock_google_search
    
    def test_validate_tool(self):
        """Test tool validation"""
        loader = ToolLoader()
        
        def valid_tool(x, y):
            return x + y
        
        assert loader.validate_tool(valid_tool) == True
        assert loader.validate_tool("not_a_function") == False
    
    def test_load_multiple_tools(self):
        """Test loading multiple tools"""
        loader = ToolLoader()
        specs = [
            {"name": "tool1", "source": "inline", "definition": "def tool1(x): return x"},
            {"name": "tool2", "source": "inline", "definition": "def tool2(x): return x * 2"}
        ]
        
        tools = loader.load_tools(specs)
        assert len(tools) == 2
        assert all(callable(tool) for tool in tools)