"""Comprehensive tests for the TahoeOrchestrator"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.orchestrator import TahoeOrchestrator
from src.models.api import AnalysisResult
from src.services.aggregation import AnalysisResult as AggregationResult


@pytest.fixture
async def orchestrator():
    """Create orchestrator instance with mocked dependencies"""
    orch = TahoeOrchestrator()
    
    # Mock database
    orch.db = AsyncMock()
    orch.db.analysis = AsyncMock()
    orch.db.scorecard = AsyncMock()
    orch.db.agenttemplate = AsyncMock()
    
    # Mock Redis cache
    orch.cache = AsyncMock()
    orch.cache.setex = AsyncMock()
    orch.cache.get = AsyncMock(return_value=None)
    orch.cache.delete = AsyncMock()
    
    # Mark as initialized
    orch._initialized = True
    
    # Initialize services
    from src.agents.factory import AgentFactory
    from src.services.content_analyzer import ContentAnalyzer
    from src.services.aggregation import ResultAggregator
    
    orch.agent_factory = AgentFactory()
    orch.content_analyzer = ContentAnalyzer()
    orch.result_aggregator = ResultAggregator()
    
    return orch


@pytest.fixture
def sample_interaction():
    """Sample interaction data for testing"""
    return {
        "id": "test-interaction-001",
        "type": "collection_call",
        "content": "Hello, this is regarding your outstanding debt payment of $500. We need to discuss collection arrangements.",
        "metadata": {
            "duration": 180,
            "participants": 2,
            "timestamp": "2025-08-13T10:00:00Z"
        }
    }


@pytest.fixture
def sample_scorecard():
    """Sample scorecard configuration"""
    return {
        "id": "test-scorecard-001",
        "name": "FDCPA Compliance Scorecard",
        "description": "Scorecard for FDCPA compliance checking",
        "portfolioId": "test-portfolio-001",
        "version": 1,
        "requirements": {
            "mini_miranda": True,
            "time_restrictions": True
        },
        "thresholds": {
            "pass": 85,
            "fail": 60
        },
        "aggregationRules": {
            "method": "weighted_average",
            "weights": {
                "compliance": 0.5,
                "quality": 0.3
            }
        },
        "isActive": True,
        "scorecardAgents": [
            {
                "id": "sa-001",
                "scorecardId": "test-scorecard-001",
                "agentId": "agent-001",
                "weight": 1.0,
                "isRequired": True,
                "configuration": {},
                "executionOrder": 0,
                "agent": {
                    "id": "agent-001",
                    "name": "compliance_analyst",
                    "description": "Compliance analysis agent",
                    "type": "compliance",
                    "model": "gemini-2.0-flash",
                    "modelConfig": {"temperature": 0.3},
                    "capabilities": ["fdcpa", "tcpa"],
                    "tools": [],
                    "triggerRules": {
                        "content_type": ["collection_call"],
                        "regulatory_indicators": ["fdcpa"]
                    },
                    "systemPrompt": "Analyze for compliance",
                    "userPrompt": "Check this interaction",
                    "version": 1,
                    "isActive": True
                }
            },
            {
                "id": "sa-002",
                "scorecardId": "test-scorecard-001",
                "agentId": "agent-002",
                "weight": 0.8,
                "isRequired": False,
                "configuration": {},
                "executionOrder": 1,
                "agent": {
                    "id": "agent-002",
                    "name": "quality_assessor",
                    "description": "Quality assessment agent",
                    "type": "quality",
                    "model": "gemini-2.0-flash",
                    "modelConfig": {"temperature": 0.5},
                    "capabilities": ["quality", "empathy"],
                    "tools": [],
                    "triggerRules": {},
                    "systemPrompt": "Assess quality",
                    "userPrompt": "Rate quality",
                    "version": 1,
                    "isActive": True
                }
            }
        ]
    }


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    orch = TahoeOrchestrator()
    assert orch.db is None
    assert orch.cache is None
    assert orch._initialized is False
    
    # Mock Prisma and Redis
    with patch('src.orchestrator.Prisma') as mock_prisma:
        with patch('src.orchestrator.redis.from_url') as mock_redis:
            mock_prisma_instance = AsyncMock()
            mock_prisma.return_value = mock_prisma_instance
            
            await orch.initialize()
            
            assert orch._initialized is True
            assert orch.db is not None
            assert orch.cache is not None
            assert orch.agent_factory is not None
            assert orch.content_analyzer is not None
            assert orch.result_aggregator is not None


@pytest.mark.asyncio
async def test_analyze_interaction_complete_workflow(orchestrator, sample_interaction, sample_scorecard):
    """Test complete analysis workflow"""
    # Setup mocks
    orchestrator.db.analysis.create.return_value = Mock(
        id="analysis-001",
        status="processing",
        traceId="trace-001"
    )
    
    orchestrator.db.analysis.update.return_value = Mock(
        id="analysis-001",
        status="complete"
    )
    
    orchestrator.db.scorecard.find_unique.return_value = sample_scorecard
    
    # Execute analysis
    result = await orchestrator.analyze_interaction(
        interaction_data=sample_interaction,
        scorecard_id="test-scorecard-001",
        portfolio_id="test-portfolio-001"
    )
    
    # Verify result
    assert isinstance(result, AggregationResult)
    assert result.overall_score > 0
    assert result.confidence > 0
    assert isinstance(result.violations, list)
    assert isinstance(result.recommendations, list)
    
    # Verify database calls
    orchestrator.db.analysis.create.assert_called_once()
    orchestrator.db.analysis.update.assert_called_once()
    
    # Verify Redis session management
    orchestrator.cache.setex.assert_called()
    orchestrator.cache.delete.assert_called()


@pytest.mark.asyncio
async def test_content_analysis_phase(orchestrator, sample_interaction):
    """Test content analysis phase"""
    analysis_id = "test-analysis-001"
    
    # Execute content analysis
    metadata = await orchestrator.analyze_content(sample_interaction, analysis_id)
    
    # Verify metadata structure
    assert "language" in metadata
    assert "interaction_type" in metadata
    assert "detected_topics" in metadata
    assert "regulatory_indicators" in metadata
    assert "complexity_score" in metadata
    
    # Verify detected content
    assert metadata["language"] == "en"
    assert metadata["interaction_type"] == "collection_call"
    assert "collection" in metadata["detected_topics"]
    assert "payment" in metadata["detected_topics"]
    assert "fdcpa" in metadata["regulatory_indicators"]
    assert 0 <= metadata["complexity_score"] <= 1


@pytest.mark.asyncio
async def test_agent_selection(orchestrator, sample_scorecard):
    """Test agent selection based on trigger rules"""
    content_metadata = {
        "interaction_type": "collection_call",
        "detected_topics": ["collection", "payment"],
        "regulatory_indicators": ["fdcpa"],
        "complexity_score": 0.6
    }
    
    # Execute agent selection
    selected_agents = await orchestrator.select_agents(
        scorecard=sample_scorecard,
        content_metadata=content_metadata,
        portfolio_id="test-portfolio-001"
    )
    
    # Verify selection
    assert len(selected_agents) == 2  # Both agents should be selected
    assert selected_agents[0]["template"]["name"] == "compliance_analyst"
    assert selected_agents[1]["template"]["name"] == "quality_assessor"
    
    # Verify execution order
    assert selected_agents[0]["execution_order"] == 0
    assert selected_agents[1]["execution_order"] == 1


@pytest.mark.asyncio
async def test_agent_selection_with_filtering(orchestrator, sample_scorecard):
    """Test agent selection filters based on trigger rules"""
    content_metadata = {
        "interaction_type": "email",  # Not a collection_call
        "detected_topics": ["dispute"],
        "regulatory_indicators": [],
        "complexity_score": 0.3
    }
    
    # Execute agent selection
    selected_agents = await orchestrator.select_agents(
        scorecard=sample_scorecard,
        content_metadata=content_metadata,
        portfolio_id="test-portfolio-001"
    )
    
    # Only quality agent should be selected (no trigger rules)
    assert len(selected_agents) == 1
    assert selected_agents[0]["template"]["name"] == "quality_assessor"


@pytest.mark.asyncio
async def test_execution_plan_building(orchestrator):
    """Test execution plan building"""
    agents = [
        {"template": {"name": "agent1"}, "execution_order": 0},
        {"template": {"name": "agent2"}, "execution_order": 0},
        {"template": {"name": "agent3"}, "execution_order": 1},
        {"template": {"name": "agent4"}, "execution_order": 2},
        {"template": {"name": "agent5"}, "execution_order": 2}
    ]
    
    plan = orchestrator.build_execution_plan(agents)
    
    # Verify plan structure
    assert len(plan["parallel_phase"]) == 2  # agent1 and agent2
    assert len(plan["sequential_phases"]) == 2  # Two sequential groups
    assert plan["total_agents"] == 5
    
    # Verify sequential grouping
    assert len(plan["sequential_phases"][0]) == 1  # agent3
    assert len(plan["sequential_phases"][1]) == 2  # agent4 and agent5


@pytest.mark.asyncio
async def test_agent_execution_with_timeout(orchestrator, sample_interaction):
    """Test agent execution with timeout handling"""
    # Create agent that times out
    timeout_agent = AsyncMock()
    timeout_agent.analyze = AsyncMock(side_effect=asyncio.TimeoutError())
    
    orchestrator.agent_factory.create_agent = AsyncMock(return_value=timeout_agent)
    
    agent_config = {
        "template": {"name": "timeout_agent"},
        "execution_order": 0
    }
    
    # Execute and expect timeout error
    with pytest.raises(Exception) as exc_info:
        await orchestrator._execute_single_agent(
            agent_config=agent_config,
            interaction_data=sample_interaction,
            trace_id="test-trace"
        )
    
    assert "timed out" in str(exc_info.value)


@pytest.mark.asyncio
async def test_parallel_agent_execution(orchestrator, sample_interaction):
    """Test parallel execution of multiple agents"""
    execution_plan = {
        "parallel_phase": [
            {"template": {"name": "agent1"}, "execution_order": 0},
            {"template": {"name": "agent2"}, "execution_order": 0}
        ],
        "sequential_phases": [],
        "total_agents": 2
    }
    
    # Execute agents
    results = await orchestrator.execute_agents(
        execution_plan=execution_plan,
        interaction_data=sample_interaction,
        analysis_id="test-analysis",
        trace_id="test-trace"
    )
    
    # Verify both agents executed
    assert len(results) == 2
    assert "agent1" in results
    assert "agent2" in results
    
    # Verify results structure
    for agent_name, result in results.items():
        assert "score" in result
        assert "confidence" in result


@pytest.mark.asyncio
async def test_result_aggregation(orchestrator, sample_scorecard):
    """Test result aggregation"""
    agent_results = {
        "compliance_analyst": {
            "score": 88.5,
            "confidence": 0.92,
            "violations": [{"regulation": "FDCPA", "severity": "low"}],
            "recommendations": []
        },
        "quality_assessor": {
            "score": 82.0,
            "confidence": 0.88,
            "violations": [],
            "recommendations": [{"category": "quality", "priority": "low"}]
        }
    }
    
    # Execute aggregation
    result = await orchestrator.aggregate_results(
        agent_results=agent_results,
        scorecard=sample_scorecard,
        analysis_id="test-analysis"
    )
    
    # Verify aggregated result
    assert isinstance(result, AggregationResult)
    assert result.overall_score > 0
    assert result.confidence > 0
    assert len(result.violations) == 1
    assert len(result.recommendations) == 1


@pytest.mark.asyncio
async def test_scorecard_caching(orchestrator, sample_scorecard):
    """Test scorecard caching mechanism"""
    scorecard_id = "test-scorecard-001"
    
    # First call - should load from database
    orchestrator.db.scorecard.find_unique.return_value = sample_scorecard
    result1 = await orchestrator.load_scorecard(scorecard_id)
    
    # Verify database was called
    orchestrator.db.scorecard.find_unique.assert_called_once()
    
    # Verify cache was set
    orchestrator.cache.setex.assert_called()
    cache_call_args = orchestrator.cache.setex.call_args
    assert cache_call_args[0][0] == f"scorecard:{scorecard_id}"
    assert cache_call_args[0][1] == 300  # 5 minute TTL
    
    # Second call - should use cache
    orchestrator.cache.get.return_value = json.dumps(sample_scorecard)
    orchestrator.db.scorecard.find_unique.reset_mock()
    
    result2 = await orchestrator.load_scorecard(scorecard_id)
    
    # Database should not be called again
    orchestrator.db.scorecard.find_unique.assert_not_called()


@pytest.mark.asyncio
async def test_session_phase_tracking(orchestrator):
    """Test Redis session phase tracking"""
    analysis_id = "test-analysis"
    phase = "content_analysis"
    
    # Setup existing session
    existing_session = {
        "status": "processing",
        "phase": "initialization",
        "started_at": "2025-08-13T10:00:00"
    }
    orchestrator.cache.get.return_value = json.dumps(existing_session)
    
    # Update phase
    await orchestrator._update_session_phase(analysis_id, phase)
    
    # Verify cache was updated
    orchestrator.cache.setex.assert_called()
    updated_call = orchestrator.cache.setex.call_args
    updated_data = json.loads(updated_call[0][2])
    
    assert updated_data["phase"] == phase
    assert updated_data["status"] == "processing"  # Should preserve other fields


@pytest.mark.asyncio
async def test_error_handling_and_cleanup(orchestrator, sample_interaction):
    """Test error handling and cleanup on failure"""
    # Setup mock to fail during execution
    orchestrator.db.analysis.create.return_value = Mock(
        id="analysis-001",
        status="processing"
    )
    
    # Make content analyzer fail
    orchestrator.content_analyzer.extract_topics = AsyncMock(
        side_effect=Exception("Analysis failed")
    )
    
    # Execute and expect failure
    with pytest.raises(Exception) as exc_info:
        await orchestrator.analyze_interaction(
            interaction_data=sample_interaction,
            scorecard_id="test-scorecard",
            portfolio_id="test-portfolio"
        )
    
    assert "Analysis failed" in str(exc_info.value)
    
    # Verify cleanup
    orchestrator.db.analysis.update.assert_called()
    update_call = orchestrator.db.analysis.update.call_args
    assert update_call[1]["data"]["status"] == "failed"
    
    # Verify Redis session was deleted
    orchestrator.cache.delete.assert_called()


@pytest.mark.asyncio
async def test_trigger_rule_evaluation():
    """Test _should_activate_agent trigger rule logic"""
    orch = TahoeOrchestrator()
    
    # Test with no trigger rules - should activate
    agent_template = {"name": "test_agent", "triggerRules": {}}
    content_metadata = {"interaction_type": "call"}
    assert orch._should_activate_agent(agent_template, content_metadata) is True
    
    # Test content type match
    agent_template = {
        "triggerRules": {"content_type": ["call", "email"]}
    }
    content_metadata = {"interaction_type": "call"}
    assert orch._should_activate_agent(agent_template, content_metadata) is True
    
    # Test content type mismatch
    content_metadata = {"interaction_type": "chat"}
    assert orch._should_activate_agent(agent_template, content_metadata) is False
    
    # Test topic requirements
    agent_template = {
        "triggerRules": {"required_topics": ["payment", "collection"]}
    }
    content_metadata = {
        "interaction_type": "call",
        "detected_topics": ["payment", "dispute"]
    }
    assert orch._should_activate_agent(agent_template, content_metadata) is True
    
    # Test regulatory indicators
    agent_template = {
        "triggerRules": {"regulatory_indicators": ["fdcpa"]}
    }
    content_metadata = {
        "interaction_type": "call",
        "regulatory_indicators": ["fdcpa", "tcpa"]
    }
    assert orch._should_activate_agent(agent_template, content_metadata) is True
    
    # Test multiple criteria
    agent_template = {
        "triggerRules": {
            "content_type": ["call"],
            "required_topics": ["collection"],
            "regulatory_indicators": ["fdcpa"]
        }
    }
    content_metadata = {
        "interaction_type": "call",
        "detected_topics": ["collection"],
        "regulatory_indicators": ["fdcpa"]
    }
    assert orch._should_activate_agent(agent_template, content_metadata) is True
    
    # One criteria fails
    content_metadata["interaction_type"] = "email"
    assert orch._should_activate_agent(agent_template, content_metadata) is False


@pytest.mark.asyncio
async def test_group_by_execution_order():
    """Test _group_by_execution_order helper method"""
    orch = TahoeOrchestrator()
    
    agents = [
        {"name": "agent1", "execution_order": 1},
        {"name": "agent2", "execution_order": 2},
        {"name": "agent3", "execution_order": 1},
        {"name": "agent4", "execution_order": 3},
        {"name": "agent5", "execution_order": 2}
    ]
    
    grouped = orch._group_by_execution_order(agents)
    
    # Should have 3 groups
    assert len(grouped) == 3
    
    # First group (order 1)
    assert len(grouped[0]) == 2
    assert grouped[0][0]["name"] in ["agent1", "agent3"]
    
    # Second group (order 2)
    assert len(grouped[1]) == 2
    assert grouped[1][0]["name"] in ["agent2", "agent5"]
    
    # Third group (order 3)
    assert len(grouped[2]) == 1
    assert grouped[2][0]["name"] == "agent4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])