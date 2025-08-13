"""Tests for AgentFactory and related components."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

from src.agents.factory import AgentFactory, TahoeAgent, TemplateNotFoundError
from src.agents.base import AgentResult
from src.models.registry import ModelRegistry, ModelConfig
from src.tools.registry import ToolRegistry


class MockPrismaTemplate:
    """Mock Prisma template object"""
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-template-id")
        self.name = kwargs.get("name", "test-agent")
        self.description = kwargs.get("description", "Test agent description")
        self.type = kwargs.get("type", "specialist")
        self.model = kwargs.get("model", "gemini-2.0-flash")
        self.modelConfig = kwargs.get("modelConfig", {})
        self.capabilities = kwargs.get("capabilities", ["test-capability"])
        self.tools = kwargs.get("tools", ["test-tool"])
        self.triggerRules = kwargs.get("triggerRules", {})
        self.systemPrompt = kwargs.get("systemPrompt", "You are a test agent.")
        self.userPrompt = kwargs.get("userPrompt", "Analyze: {interaction}")
        self.version = kwargs.get("version", 1)
        self.isActive = kwargs.get("isActive", True)


@pytest.fixture
def mock_db():
    """Mock database connection"""
    db = AsyncMock()
    db.connect = AsyncMock()
    return db


@pytest.fixture
def mock_cache():
    """Mock Redis cache"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.setex = AsyncMock()
    cache.delete = AsyncMock()
    return cache


@pytest.fixture
def agent_factory(mock_db, mock_cache):
    """Agent factory with mocked dependencies"""
    factory = AgentFactory(db=mock_db, cache=mock_cache)
    return factory


@pytest.fixture
def sample_template():
    """Sample agent template"""
    return {
        "id": "test-template-id",
        "name": "test-agent",
        "description": "Test agent description",
        "type": "specialist",
        "model": "gemini-2.0-flash",
        "modelConfig": {"temperature": 0.3},
        "capabilities": ["test-capability"],
        "tools": ["test-tool"],
        "triggerRules": {},
        "systemPrompt": "You are a test agent.",
        "userPrompt": "Analyze: {interaction}",
        "version": 1,
        "isActive": True
    }


class TestModelRegistry:
    """Test ModelRegistry functionality"""
    
    def test_get_config_gemini(self):
        """Test getting Gemini model configuration"""
        registry = ModelRegistry()
        
        config = registry.get_config("gemini-2.0-flash")
        
        assert config.model_string == "gemini-2.0-flash"
        assert config.provider == "gemini"
        assert config.parameters["temperature"] == 0.3
        assert config.parameters["max_tokens"] == 2000
    
    def test_get_config_with_overrides(self):
        """Test model configuration with parameter overrides"""
        registry = ModelRegistry()
        
        config = registry.get_config("gemini-2.0-flash", {"temperature": 0.7})
        
        assert config.parameters["temperature"] == 0.7
        assert config.parameters["max_tokens"] == 2000  # Default preserved
    
    def test_get_config_unknown_model(self):
        """Test error handling for unknown models"""
        registry = ModelRegistry()
        
        with pytest.raises(ValueError, match="Cannot determine provider"):
            registry.get_config("unknown-model")
    
    def test_provider_detection(self):
        """Test provider detection from model names"""
        registry = ModelRegistry()
        
        assert registry._get_provider("gemini-2.0-flash") == "gemini"
        assert registry._get_provider("gpt-4-turbo") == "openai"
        assert registry._get_provider("claude-3-opus") == "anthropic"
    
    @pytest.mark.asyncio
    async def test_check_model_availability(self):
        """Test model availability checking"""
        registry = ModelRegistry()
        
        # Known model should be available
        assert await registry.check_model_availability("gemini-2.0-flash") == True
        
        # Unknown model should not be available
        assert await registry.check_model_availability("unknown-model") == False


class TestToolRegistry:
    """Test ToolRegistry functionality"""
    
    @pytest.mark.asyncio
    async def test_load_tools(self):
        """Test loading tools by IDs"""
        registry = ToolRegistry()
        
        tools = await registry.load_tools(["regulatory_lookup", "compliance_check"])
        
        assert len(tools) == 2
        assert tools[0]["name"] == "regulatory_lookup"
        assert tools[1]["name"] == "compliance_check"
    
    @pytest.mark.asyncio
    async def test_get_tool(self):
        """Test getting single tool"""
        registry = ToolRegistry()
        
        tool = await registry.get_tool("regulatory_lookup")
        
        assert tool is not None
        assert tool["name"] == "regulatory_lookup"
        assert tool["type"] == "function"
    
    @pytest.mark.asyncio
    async def test_get_unknown_tool(self):
        """Test getting unknown tool returns None"""
        registry = ToolRegistry()
        
        tool = await registry.get_tool("unknown-tool")
        
        assert tool is None


class TestAgentFactory:
    """Test AgentFactory functionality"""
    
    @pytest.mark.asyncio
    async def test_initialize(self, agent_factory, mock_db):
        """Test factory initialization"""
        # Test that factory uses provided db/cache instead of creating new ones
        await agent_factory.initialize()
        
        # Should use the provided mocked db and cache
        assert agent_factory.db == mock_db
        assert agent_factory.cache is not None
    
    @pytest.mark.asyncio
    async def test_load_template_from_cache(self, agent_factory, mock_cache, sample_template):
        """Test loading template from cache"""
        # Setup cache hit
        mock_cache.get.return_value = json.dumps(sample_template)
        
        result = await agent_factory.load_template("test-template-id")
        
        assert result == sample_template
        mock_cache.get.assert_called_once_with("agent:template:test-template-id")
    
    @pytest.mark.asyncio
    async def test_load_template_from_database(self, agent_factory, mock_db, mock_cache, sample_template):
        """Test loading template from database"""
        # Setup cache miss and database hit
        mock_cache.get.return_value = None
        mock_template = MockPrismaTemplate(**sample_template)
        mock_db.agenttemplate.find_unique.return_value = mock_template
        
        result = await agent_factory.load_template("test-template-id")
        
        assert result["name"] == sample_template["name"]
        assert result["model"] == sample_template["model"]
        mock_cache.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_template_not_found(self, agent_factory, mock_db, mock_cache):
        """Test error handling when template not found"""
        # Setup cache miss and database miss
        mock_cache.get.return_value = None
        mock_db.agenttemplate.find_unique.return_value = None
        
        with pytest.raises(TemplateNotFoundError):
            await agent_factory.load_template("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_load_template_inactive(self, agent_factory, mock_db, mock_cache, sample_template):
        """Test error handling for inactive templates"""
        # Setup inactive template
        mock_cache.get.return_value = None
        inactive_template = MockPrismaTemplate(**{**sample_template, "isActive": False})
        mock_db.agenttemplate.find_unique.return_value = inactive_template
        
        with pytest.raises(ValueError, match="inactive"):
            await agent_factory.load_template("test-template-id")
    
    @pytest.mark.asyncio
    async def test_create_agent(self, agent_factory, sample_template):
        """Test creating agent from template"""
        with patch('src.agents.factory.LlmAgent') as mock_llm_agent:
            mock_adk_agent = AsyncMock()
            mock_llm_agent.return_value = mock_adk_agent
            
            agent = await agent_factory.create_agent(sample_template)
            
            assert isinstance(agent, TahoeAgent)
            assert agent.template == sample_template
            assert agent.factory == agent_factory
            mock_llm_agent.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_agent_invalid_model(self, agent_factory, sample_template):
        """Test error handling for invalid model"""
        invalid_template = {**sample_template, "model": "invalid-model"}
        
        with pytest.raises(ValueError, match="Agent creation failed"):
            await agent_factory.create_agent(invalid_template)
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self, agent_factory, mock_cache):
        """Test cache invalidation"""
        await agent_factory.invalidate_cache("test-template-id")
        
        mock_cache.delete.assert_called_once_with("agent:template:test-template-id")


class TestTahoeAgent:
    """Test TahoeAgent functionality"""
    
    @pytest.fixture
    def mock_adk_agent(self):
        """Mock ADK agent"""
        agent = AsyncMock()
        agent.run.return_value = "Test analysis result with score: 85% and recommendations to improve"
        return agent
    
    @pytest.fixture
    def tahoe_agent(self, mock_adk_agent, sample_template, agent_factory):
        """TahoeAgent instance for testing"""
        return TahoeAgent(
            adk_agent=mock_adk_agent,
            template=sample_template,
            factory=agent_factory
        )
    
    @pytest.mark.asyncio
    async def test_analyze_success(self, tahoe_agent, mock_adk_agent):
        """Test successful analysis"""
        input_data = {
            "interaction": {"content": "Test interaction content", "type": "call"},
            "trace_id": "test-trace-123"
        }
        
        result = await tahoe_agent.analyze(input_data)
        
        assert isinstance(result, AgentResult)
        assert result.agent_name == "test-agent"
        assert result.agent_version == "1"
        assert result.score > 0  # Should extract score from mock response
        assert result.execution_time > 0
        assert result.metadata["trace_id"] == "test-trace-123"
        mock_adk_agent.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_error_handling(self, tahoe_agent, mock_adk_agent):
        """Test error handling during analysis"""
        # Make ADK agent raise exception
        mock_adk_agent.run.side_effect = Exception("ADK error")
        
        input_data = {
            "interaction": {"content": "Test content"},
            "trace_id": "test-trace-123"
        }
        
        result = await tahoe_agent.analyze(input_data)
        
        assert isinstance(result, AgentResult)
        assert result.score == 0.0
        assert result.confidence == 0.0
        assert "error" in result.metadata
    
    def test_build_user_prompt_with_template(self, tahoe_agent):
        """Test building user prompt with template"""
        input_data = {
            "interaction": {"content": "Test content"},
            "configuration": {"setting": "value"},
            "context": {"previous": "result"}
        }
        
        prompt = tahoe_agent._build_user_prompt(input_data)
        
        # Should use template format
        assert "Test content" in str(prompt)
    
    def test_build_user_prompt_fallback(self, tahoe_agent):
        """Test user prompt fallback when template fails"""
        # Remove userPrompt to test fallback
        tahoe_agent.template["userPrompt"] = ""
        
        input_data = {
            "interaction": {"content": "Test content", "type": "call"}
        }
        
        prompt = tahoe_agent._build_user_prompt(input_data)
        
        assert "call interaction" in prompt
        assert "Test content" in prompt
    
    def test_extract_score(self, tahoe_agent):
        """Test score extraction from text"""
        # Test various score formats
        assert tahoe_agent._extract_score("Score: 85") == 85.0
        assert tahoe_agent._extract_score("Rating is 90%") == 90.0
        assert tahoe_agent._extract_score("8.5/10 overall") == 85.0
        assert tahoe_agent._extract_score("No score here") == 0.0
    
    def test_calculate_confidence(self, tahoe_agent):
        """Test confidence calculation"""
        # Test various confidence indicators - need longer strings to avoid length check
        long_confident = "I am very confident this is correct and accurate based on my thorough analysis of the data"
        long_uncertain = "Maybe this is right but I am uncertain about the conclusion given the limited information available"
        
        assert tahoe_agent._calculate_confidence(long_confident) > 0.8
        assert tahoe_agent._calculate_confidence(long_uncertain) < 0.7
        assert tahoe_agent._calculate_confidence("Short") < 0.5
        assert tahoe_agent._calculate_confidence("Normal length response with good content that meets minimum requirements") == 0.85
    
    def test_extract_violations(self, tahoe_agent):
        """Test violation extraction"""
        result_with_violation = "This contains a violation of policy"
        violations = tahoe_agent._extract_violations(result_with_violation)
        
        assert len(violations) == 1
        assert violations[0]["type"] == "detected_violation"
        
        result_without_violation = "Everything looks good"
        violations = tahoe_agent._extract_violations(result_without_violation)
        
        assert len(violations) == 0
    
    def test_extract_recommendations(self, tahoe_agent):
        """Test recommendation extraction"""
        result_with_rec = "I recommend improving the process"
        recommendations = tahoe_agent._extract_recommendations(result_with_rec)
        
        assert len(recommendations) == 1
        assert recommendations[0]["category"] == "general"
        
        result_without_rec = "Analysis complete"
        recommendations = tahoe_agent._extract_recommendations(result_without_rec)
        
        assert len(recommendations) == 0


@pytest.mark.asyncio
async def test_integration_create_and_analyze(mock_db, mock_cache, sample_template):
    """Integration test for creating and analyzing with agent"""
    # Setup mocks
    mock_cache.get.return_value = None
    mock_template_obj = MockPrismaTemplate(**sample_template)
    mock_db.agenttemplate.find_unique.return_value = mock_template_obj
    
    # Create factory and agent
    factory = AgentFactory(db=mock_db, cache=mock_cache)
    
    with patch('src.agents.factory.LlmAgent') as mock_llm_agent:
        mock_adk_agent = AsyncMock()
        mock_adk_agent.run.return_value = "Compliance analysis complete. Score: 88%. I recommend reviewing procedures."
        mock_llm_agent.return_value = mock_adk_agent
        
        # Load template and create agent
        template = await factory.load_template("test-template-id")
        agent = await factory.create_agent(template)
        
        # Test analysis
        input_data = {
            "interaction": {"content": "Test call transcript", "type": "call"},
            "trace_id": "integration-test-123"
        }
        
        result = await agent.analyze(input_data)
        
        assert isinstance(result, AgentResult)
        assert result.agent_name == "test-agent"
        assert result.score == 88.0  # Should extract from mock response
        assert len(result.recommendations) > 0  # Should detect recommendation
        assert result.metadata["trace_id"] == "integration-test-123"