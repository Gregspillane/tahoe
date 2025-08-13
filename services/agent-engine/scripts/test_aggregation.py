#!/usr/bin/env python3
"""Test script for Result Aggregation functionality"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.aggregation import ResultAggregator, AnalysisResult


async def test_aggregation():
    """Test the aggregation service with sample data"""
    
    print("=" * 60)
    print("Testing Result Aggregation Service")
    print("=" * 60)
    
    # Load test fixtures
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures" / "agent_results.json"
    with open(fixtures_path) as f:
        fixtures = json.load(f)
    
    # Initialize aggregator
    aggregator = ResultAggregator()
    print("\n✓ ResultAggregator initialized")
    
    # Test 1: Full analysis with all agents successful
    print("\n" + "-" * 40)
    print("Test 1: Full Analysis (4 agents)")
    print("-" * 40)
    
    agent_results = fixtures["full_analysis"]
    
    aggregation_rules = {
        "method": "weighted_average",
        "weights": {
            "compliance_specialist": 0.4,
            "quality_specialist": 0.25,
            "identity_specialist": 0.2,
            "risk_specialist": 0.15
        },
        "version": 1
    }
    
    thresholds = {
        "pass": 80,
        "review": 65,
        "critical_auto_fail": True,
        "max_score_with_critical": 50,
        "high_violation_threshold": 3,
        "high_violation_penalty": 10
    }
    
    result = await aggregator.aggregate(agent_results, aggregation_rules, thresholds)
    
    print(f"\nAnalysis ID: {result.analysis_id}")
    print(f"Overall Score: {result.overall_score}/100")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Status: {result.status}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    
    print(f"\nViolations Found: {len(result.violations)}")
    for v in result.violations:
        print(f"  - [{v['severity'].upper()}] {v.get('regulation', 'N/A')}: {v['description'][:50]}...")
    
    print(f"\nRecommendations: {len(result.recommendations)}")
    for r in result.recommendations[:3]:  # Show top 3
        print(f"  - [{r['priority'].upper()}] {r['action'][:60]}...")
    
    print(f"\nPer-Agent Results:")
    for agent, details in result.categories.items():
        print(f"  - {agent}: Score={details['score']}, Confidence={details['confidence']:.2%}")
    
    print(f"\nAudit Trail:")
    print(f"  - Agents Executed: {result.audit_trail['agents_executed']}")
    print(f"  - Successful: {result.audit_trail['agents_successful']}")
    print(f"  - Failed: {result.audit_trail['agents_failed']}")
    print(f"  - Method: {result.audit_trail['aggregation_method']}")
    
    # Test 2: Partial analysis with one agent failure
    print("\n" + "-" * 40)
    print("Test 2: Partial Analysis (1 agent failed)")
    print("-" * 40)
    
    agent_results = fixtures["partial_analysis"]
    
    result = await aggregator.aggregate(agent_results, aggregation_rules, thresholds)
    
    print(f"\nOverall Score: {result.overall_score}/100")
    print(f"Status: {result.status}")
    print(f"Successful Agents: {result.audit_trail['agents_successful']}")
    print(f"Failed Agents: {result.audit_trail['agents_failed']}")
    if result.audit_trail['failed_agents']:
        for failed in result.audit_trail['failed_agents']:
            print(f"  - {failed['name']}: {failed['error']}")
    
    # Test 3: Critical violation scenario
    print("\n" + "-" * 40)
    print("Test 3: Critical Violation Scenario")
    print("-" * 40)
    
    agent_results = fixtures["critical_violation_analysis"]
    
    result = await aggregator.aggregate(agent_results, aggregation_rules, thresholds)
    
    print(f"\nOriginal Score (before rules): Would be ~{(45*0.4 + 70*0.25)/(0.4+0.25):.1f}")
    print(f"Adjusted Score: {result.overall_score}/100")
    print(f"Status: {result.status}")
    print(f"Reason: Critical violation detected - auto-fail applied")
    
    critical_violations = [v for v in result.violations if v['severity'] == 'critical']
    for v in critical_violations:
        print(f"\nCritical Violation:")
        print(f"  - Regulation: {v.get('regulation', 'N/A')}")
        print(f"  - Description: {v['description']}")
    
    # Test 4: Weight calculation details
    print("\n" + "-" * 40)
    print("Test 4: Weight Calculation Details")
    print("-" * 40)
    
    agent_results = {
        "agent_a": {"score": 90, "confidence": 0.95},
        "agent_b": {"score": 70, "confidence": 0.85},
        "agent_c": {"score": 80, "confidence": 0.90}
    }
    
    rules = {
        "weights": {
            "agent_a": 0.5,
            "agent_b": 0.3,
            "agent_c": 0.2
        }
    }
    
    score, details = aggregator._calculate_weighted_score(agent_results, rules)
    
    print(f"\nWeighted Score Calculation:")
    print(f"  Agent A: 90 × 0.5 = {details['weighted_contributions']['agent_a']}")
    print(f"  Agent B: 70 × 0.3 = {details['weighted_contributions']['agent_b']}")
    print(f"  Agent C: 80 × 0.2 = {details['weighted_contributions']['agent_c']}")
    print(f"  Total Weight: {details['total_weight']}")
    print(f"  Weighted Sum: {details['weighted_sum']}")
    print(f"  Final Score: {score}")
    
    # Test 5: Serialization
    print("\n" + "-" * 40)
    print("Test 5: Result Serialization")
    print("-" * 40)
    
    agent_results = fixtures["full_analysis"]
    result = await aggregator.aggregate(agent_results, aggregation_rules, thresholds)
    
    # Convert to dict
    result_dict = result.to_dict()
    
    # Serialize to JSON
    json_str = json.dumps(result_dict, indent=2, default=str)
    
    print(f"\nSerialized result preview (first 500 chars):")
    print(json_str[:500] + "...")
    
    print("\n" + "=" * 60)
    print("✓ All aggregation tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_aggregation())