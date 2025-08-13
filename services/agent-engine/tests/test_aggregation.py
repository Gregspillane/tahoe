"""Tests for Result Aggregation Service"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from src.services.aggregation import ResultAggregator, AnalysisResult


class TestResultAggregator:
    """Test suite for ResultAggregator"""
    
    @pytest.fixture
    def aggregator(self):
        """Create ResultAggregator instance"""
        return ResultAggregator()
    
    @pytest.fixture
    def sample_agent_results(self):
        """Sample TahoeAgent dict outputs"""
        return {
            "compliance_specialist": {
                "agent_name": "compliance_specialist",
                "agent_version": "1.0",
                "result": "Analysis complete. Score: 75. Found 2 violations.",
                "score": 75.0,
                "confidence": 0.85,
                "execution_time": 2.3,
                "model_used": "gemini-2.0-flash",
                "trace_id": "trace-001",
                "violations": [
                    {
                        "type": "regulatory",
                        "regulation": "FINRA 2210",
                        "section": "2210.d.1",
                        "description": "Missing required disclosures",
                        "severity": "high",
                        "evidence": "Line 45: No risk disclosure present"
                    },
                    {
                        "type": "regulatory",
                        "regulation": "SEC Rule 17a-4",
                        "section": "17a-4.f.2",
                        "description": "Incomplete record retention policy",
                        "severity": "medium"
                    }
                ],
                "recommendations": [
                    {
                        "category": "compliance",
                        "action": "Add required risk disclosures",
                        "priority": "high",
                        "impact": "critical",
                        "rationale": "Required by FINRA regulations"
                    }
                ],
                "findings": [
                    {"type": "violation", "summary": "Missing disclosures"},
                    {"type": "observation", "summary": "Good authentication practices"}
                ]
            },
            "quality_specialist": {
                "agent_name": "quality_specialist",
                "agent_version": "1.0",
                "result": "Quality assessment: 8.5/10",
                "confidence": 0.92,
                "execution_time": 1.8,
                "model_used": "gemini-2.0-flash",
                "trace_id": "trace-002",
                "violations": [
                    {
                        "type": "quality",
                        "description": "Poor call handling procedures",
                        "severity": "medium"
                    }
                ],
                "recommendations": [
                    {
                        "category": "training",
                        "action": "Implement call quality training",
                        "priority": "medium"
                    }
                ],
                "findings": []
            },
            "identity_specialist": {
                "agent_name": "identity_specialist",
                "agent_version": "1.0",
                "result": "Identity verification: PASS. Score 95%",
                "confidence": 0.88,
                "execution_time": 1.5,
                "model_used": "gemini-2.0-flash",
                "trace_id": "trace-003",
                "violations": [],
                "recommendations": [],
                "findings": [
                    {"type": "positive", "summary": "Strong KYC procedures"}
                ]
            }
        }
    
    @pytest.fixture
    def aggregation_rules(self):
        """Sample aggregation rules from scorecard"""
        return {
            "method": "weighted_average",
            "weights": {
                "compliance_specialist": 0.5,
                "quality_specialist": 0.3,
                "identity_specialist": 0.2
            },
            "version": 2,
            "business_rules": [
                "Critical violations auto-fail",
                "Cap at 50 with critical violations"
            ]
        }
    
    @pytest.fixture
    def thresholds(self):
        """Sample thresholds from scorecard"""
        return {
            "pass": 80,
            "review": 60,
            "critical_auto_fail": True,
            "max_score_with_critical": 50,
            "high_violation_threshold": 3,
            "high_violation_penalty": 10
        }
    
    @pytest.mark.asyncio
    async def test_aggregate_basic(self, aggregator, sample_agent_results, 
                                   aggregation_rules, thresholds):
        """Test basic aggregation functionality"""
        
        result = await aggregator.aggregate(
            sample_agent_results,
            aggregation_rules,
            thresholds
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.overall_score > 0
        assert 0 <= result.confidence <= 1
        assert len(result.violations) > 0
        assert len(result.recommendations) > 0
        assert len(result.categories) == 3
        assert result.status in ["PASS", "FAIL", "REVIEW"]
    
    @pytest.mark.asyncio
    async def test_weighted_scoring(self, aggregator):
        """Test weighted score calculation"""
        
        results = {
            "agent1": {"score": 80, "confidence": 0.9},
            "agent2": {"score": 60, "confidence": 0.8}
        }
        
        rules = {
            "weights": {
                "agent1": 0.7,
                "agent2": 0.3
            }
        }
        
        score, details = aggregator._calculate_weighted_score(results, rules)
        
        # Expected: (80 * 0.7 + 60 * 0.3) / (0.7 + 0.3) = 74
        assert score == 74.0
        assert details["agent_scores"]["agent1"] == 80
        assert details["agent_weights"]["agent1"] == 0.7
        assert details["overall_score"] == 74.0
    
    def test_extract_score_patterns(self, aggregator):
        """Test score extraction from various text patterns"""
        
        # Direct score field
        assert aggregator._extract_score({"score": 85}) == 85.0
        
        # Score: XX pattern
        assert aggregator._extract_score(
            {"result": "Analysis complete. Score: 75"}
        ) == 75.0
        
        # Percentage pattern
        assert aggregator._extract_score(
            {"result": "Compliance rate: 92%"}
        ) == 92.0
        
        # X/10 pattern
        assert aggregator._extract_score(
            {"result": "Quality: 8.5/10"}
        ) == 85.0
        
        # No pattern found - default
        assert aggregator._extract_score(
            {"result": "No score found"}
        ) == 50.0
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, aggregator):
        """Test confidence score aggregation"""
        
        results = {
            "agent1": {"confidence": 0.9},
            "agent2": {"confidence": 0.8},
            "agent3": {"confidence": 0.85}
        }
        
        confidence = aggregator._calculate_confidence(results)
        
        assert 0 <= confidence <= 1
        # Should be close to mean with consistency adjustment
        assert 0.7 <= confidence <= 0.95
    
    @pytest.mark.asyncio
    async def test_violation_deduplication(self, aggregator, sample_agent_results):
        """Test violation aggregation and deduplication"""
        
        violations = aggregator._aggregate_violations(sample_agent_results)
        
        # Should have violations from compliance and quality agents
        # Note: findings with type="violation" are also processed
        assert len(violations) >= 3  # At least 3 violations
        
        # Check severity ordering (high should be first)
        assert violations[0]["severity"] == "high"
        
        # Check detection tracking
        assert "compliance_specialist" in violations[0]["detected_by"]
        
        # Check aggregate confidence
        assert "aggregate_confidence" in violations[0]
    
    @pytest.mark.asyncio
    async def test_recommendation_prioritization(self, aggregator, sample_agent_results):
        """Test recommendation aggregation and prioritization"""
        
        recommendations = aggregator._aggregate_recommendations(sample_agent_results)
        
        # Should have 2 recommendations
        assert len(recommendations) == 2
        
        # High priority should be first
        assert recommendations[0]["priority"] == "high"
        
        # Check suggestion tracking
        assert "compliance_specialist" in recommendations[0]["suggested_by"]
    
    @pytest.mark.asyncio
    async def test_category_building(self, aggregator, sample_agent_results):
        """Test per-agent category result building"""
        
        categories = aggregator._build_category_results(sample_agent_results)
        
        assert len(categories) == 3
        
        # Check compliance category
        compliance = categories["compliance_specialist"]
        assert compliance["score"] == 75.0
        assert compliance["confidence"] == 0.85
        assert compliance["violations_count"] == 2
        assert compliance["recommendations_count"] == 1
        assert len(compliance["key_findings"]) > 0
    
    @pytest.mark.asyncio
    async def test_business_rules_critical_violations(self, aggregator):
        """Test business rules for critical violations"""
        
        violations = [
            {"severity": "critical", "description": "Critical issue"},
            {"severity": "high", "description": "High issue"}
        ]
        
        thresholds = {
            "max_score_with_critical": 50,
            "critical_auto_fail": True
        }
        
        # Test score capping
        adjusted_score = aggregator._apply_business_rules(85, violations, thresholds)
        assert adjusted_score == 50  # Capped due to critical
        
        # Test status determination
        status = aggregator._determine_status(85, violations, thresholds)
        assert status == "FAIL"  # Auto-fail due to critical
    
    @pytest.mark.asyncio
    async def test_business_rules_high_violations(self, aggregator):
        """Test business rules for multiple high violations"""
        
        violations = [
            {"severity": "high"} for _ in range(4)
        ]
        
        thresholds = {
            "high_violation_threshold": 3,
            "high_violation_penalty": 10
        }
        
        adjusted_score = aggregator._apply_business_rules(75, violations, thresholds)
        assert adjusted_score == 65  # 75 - 10 penalty
    
    @pytest.mark.asyncio
    async def test_status_determination(self, aggregator):
        """Test pass/fail/review status determination"""
        
        thresholds = {
            "pass": 80,
            "review": 60,
            "critical_auto_fail": True
        }
        
        # Test PASS
        status = aggregator._determine_status(85, [], thresholds)
        assert status == "PASS"
        
        # Test REVIEW
        status = aggregator._determine_status(70, [], thresholds)
        assert status == "REVIEW"
        
        # Test FAIL
        status = aggregator._determine_status(50, [], thresholds)
        assert status == "FAIL"
    
    @pytest.mark.asyncio
    async def test_audit_trail_generation(self, aggregator):
        """Test audit trail building"""
        
        agent_results = {
            "agent1": {"trace_id": "trace-1"},
            "agent2": {"error": "Timeout error", "trace_id": "trace-2"}
        }
        
        rules = {"method": "weighted", "version": 2}
        weight_details = {"overall_score": 75}
        
        audit = aggregator._build_audit_trail(
            agent_results, rules, weight_details, "PASS"
        )
        
        assert audit["agents_executed"] == 2
        assert audit["agents_successful"] == 1
        assert audit["agents_failed"] == 1
        assert audit["final_status"] == "PASS"
        assert len(audit["trace_ids"]) == 2
    
    @pytest.mark.asyncio
    async def test_empty_results_handling(self, aggregator):
        """Test handling of empty agent results"""
        
        result = await aggregator.aggregate({}, {}, {})
        
        assert result.overall_score == 0
        assert result.confidence == 0
        assert len(result.violations) == 0
        assert len(result.recommendations) == 0
    
    @pytest.mark.asyncio
    async def test_error_agent_exclusion(self, aggregator):
        """Test that agents with errors are excluded from scoring"""
        
        agent_results = {
            "agent1": {"score": 80, "confidence": 0.9},
            "agent2": {"error": "Timeout"},
            "agent3": {"score": 90, "confidence": 0.85}
        }
        
        result = await aggregator.aggregate(agent_results, {}, {})
        
        # Only 2 agents should contribute to score
        assert len(result.categories) == 2
        assert "agent2" not in result.categories
    
    @pytest.mark.asyncio
    async def test_result_serialization(self, aggregator, sample_agent_results,
                                       aggregation_rules, thresholds):
        """Test AnalysisResult to_dict serialization"""
        
        result = await aggregator.aggregate(
            sample_agent_results,
            aggregation_rules,
            thresholds
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "analysis_id" in result_dict
        assert "overall_score" in result_dict
        assert "confidence" in result_dict
        assert "status" in result_dict
        
        # Should be JSON serializable
        json_str = json.dumps(result_dict)
        assert json_str
    
    @pytest.mark.asyncio
    async def test_finding_extraction(self, aggregator):
        """Test extraction of key findings from agent results"""
        
        agent_result = {
            "findings": [
                {"summary": "Critical compliance issue"},
                {"description": "Minor documentation gap"},
                "Simple string finding"
            ]
        }
        
        findings = aggregator._extract_key_findings(agent_result)
        
        assert len(findings) == 3
        assert "Critical compliance issue" in findings
        assert "Simple string finding" in findings
    
    @pytest.mark.asyncio
    async def test_complex_aggregation(self, aggregator):
        """Test complex aggregation with mixed agent results"""
        
        # Complex scenario with various agent outputs
        agent_results = {
            "compliance": {
                "score": 45,  # Low score
                "confidence": 0.95,
                "violations": [
                    {"severity": "critical", "description": "Major violation"}
                ]
            },
            "quality": {
                "result": "Score: 88",  # Score in text
                "confidence": 0.8,
                "recommendations": [
                    {"priority": "low", "action": "Minor improvement"}
                ]
            },
            "risk": {
                "error": "Connection timeout"  # Failed agent
            }
        }
        
        rules = {
            "weights": {"compliance": 0.6, "quality": 0.4}
        }
        
        thresholds = {
            "pass": 80,
            "review": 60,
            "critical_auto_fail": True,
            "max_score_with_critical": 50
        }
        
        result = await aggregator.aggregate(agent_results, rules, thresholds)
        
        # Should cap at 50 due to critical violation
        assert result.overall_score <= 50
        # Should fail due to critical violation
        assert result.status == "FAIL"
        # Should exclude failed agent
        assert len(result.categories) == 2
        # Should have the critical violation
        assert any(v["severity"] == "critical" for v in result.violations)