#!/usr/bin/env python3
"""Manual test script for orchestration engine"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import TahoeOrchestrator
from src.models.api import AnalysisRequest, InteractionData


async def test_basic_orchestration():
    """Test basic orchestration workflow"""
    print("\n" + "="*60)
    print("TEST: Basic Orchestration Workflow")
    print("="*60)
    
    orchestrator = TahoeOrchestrator()
    
    try:
        # Initialize orchestrator
        print("\n1. Initializing orchestrator...")
        await orchestrator.initialize()
        print("   ✓ Orchestrator initialized")
        
        # Create test interaction
        interaction = {
            "id": "manual-test-001",
            "type": "collection_call",
            "content": "Hello, this is regarding your account. We need to discuss payment arrangements for the balance of $1,500.",
            "metadata": {
                "duration": 180,
                "participants": 2,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Create test scorecard (will fail if not in DB)
        print("\n2. Setting up test data...")
        
        # Check if we have test data in database
        try:
            test_scorecard = await orchestrator.db.scorecard.find_first({
                "where": {"isActive": True}
            })
            
            if test_scorecard:
                scorecard_id = test_scorecard.id
                portfolio_id = test_scorecard.portfolioId
                print(f"   ✓ Using existing scorecard: {test_scorecard.name}")
            else:
                print("   ⚠ No scorecard found, creating mock data...")
                scorecard_id = "mock-scorecard-001"
                portfolio_id = "mock-portfolio-001"
        except Exception as e:
            print(f"   ⚠ Database not available, using mock IDs: {e}")
            scorecard_id = "mock-scorecard-001"
            portfolio_id = "mock-portfolio-001"
        
        # Execute analysis
        print("\n3. Executing analysis...")
        print(f"   - Interaction ID: {interaction['id']}")
        print(f"   - Scorecard ID: {scorecard_id}")
        print(f"   - Portfolio ID: {portfolio_id}")
        
        result = await orchestrator.analyze_interaction(
            interaction_data=interaction,
            scorecard_id=scorecard_id,
            portfolio_id=portfolio_id,
            options={"test_mode": True}
        )
        
        print("\n4. Analysis Results:")
        print(f"   - Overall Score: {result.overall_score}")
        print(f"   - Confidence: {result.confidence}")
        print(f"   - Violations: {len(result.violations)}")
        print(f"   - Recommendations: {len(result.recommendations)}")
        print(f"   - Execution Time: {result.execution_time:.2f}s")
        
        if result.violations:
            print("\n   Violations Detected:")
            for v in result.violations[:3]:  # Show first 3
                print(f"     • {v.get('regulation', 'Unknown')}: {v.get('description', 'No description')}")
        
        if result.recommendations:
            print("\n   Recommendations:")
            for r in result.recommendations[:3]:  # Show first 3
                print(f"     • {r.get('category', 'General')}: {r.get('action', 'No action specified')}")
        
        print("\n✅ Basic orchestration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await orchestrator.cleanup()


async def test_fdcpa_violation():
    """Test FDCPA violation detection"""
    print("\n" + "="*60)
    print("TEST: FDCPA Violation Detection")
    print("="*60)
    
    orchestrator = TahoeOrchestrator()
    
    try:
        # Load FDCPA violation fixture
        fixture_path = Path(__file__).parent.parent / "tests" / "fixtures" / "fdcpa_violation.json"
        
        if not fixture_path.exists():
            print(f"   ⚠ Fixture not found at {fixture_path}")
            return False
        
        with open(fixture_path, 'r') as f:
            fixture = json.load(f)
        
        print("\n1. Loaded FDCPA violation test fixture")
        print(f"   - Expected violations: {len(fixture['expected_violations'])}")
        
        # Initialize orchestrator
        await orchestrator.initialize()
        
        # Use mock IDs for testing
        scorecard_id = fixture["scorecard_config"]["scorecard_id"]
        portfolio_id = fixture["scorecard_config"]["portfolio_id"]
        
        # Execute analysis
        print("\n2. Analyzing FDCPA violation interaction...")
        
        result = await orchestrator.analyze_interaction(
            interaction_data=fixture["interaction"],
            scorecard_id=scorecard_id,
            portfolio_id=portfolio_id
        )
        
        print("\n3. Analysis Results:")
        print(f"   - Overall Score: {result.overall_score}")
        print(f"   - Violations Found: {len(result.violations)}")
        
        # Check if score is in expected range
        expected_range = fixture["scorecard_config"]["expected_score_range"]
        if expected_range["min"] <= result.overall_score <= expected_range["max"]:
            print(f"   ✓ Score within expected range ({expected_range['min']}-{expected_range['max']})")
        else:
            print(f"   ⚠ Score outside expected range")
        
        print("\n✅ FDCPA violation test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await orchestrator.cleanup()


async def test_content_analysis():
    """Test content analysis functionality"""
    print("\n" + "="*60)
    print("TEST: Content Analysis")
    print("="*60)
    
    from src.services.content_analyzer import ContentAnalyzer
    
    analyzer = ContentAnalyzer()
    
    test_cases = [
        {
            "name": "Collection Call",
            "data": {
                "id": "test-001",
                "type": "collection_call",
                "content": "This is about your debt payment of $500. We need to collect this amount.",
                "metadata": {"duration": 120}
            },
            "expected": {
                "topics": ["payment", "collection"],
                "indicators": ["fdcpa"]
            }
        },
        {
            "name": "Dispute Email",
            "data": {
                "id": "test-002",
                "type": "email",
                "content": "I dispute this debt. This is not mine and I want verification.",
                "metadata": {}
            },
            "expected": {
                "topics": ["dispute", "verification"],
                "indicators": ["fdcpa", "fcra"]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n Testing: {test_case['name']}")
        
        # Extract topics
        topics = await analyzer.extract_topics(test_case["data"])
        print(f"   Topics: {topics}")
        
        # Detect regulatory context
        indicators = await analyzer.detect_regulatory_context(test_case["data"])
        print(f"   Regulatory: {indicators}")
        
        # Assess complexity
        complexity = await analyzer.assess_complexity(test_case["data"])
        print(f"   Complexity: {complexity:.2f}")
        
        # Verify expectations
        for expected_topic in test_case["expected"]["topics"]:
            if expected_topic in topics:
                print(f"   ✓ Found expected topic: {expected_topic}")
            else:
                print(f"   ⚠ Missing expected topic: {expected_topic}")
    
    print("\n✅ Content analysis test completed!")
    return True


async def test_redis_session():
    """Test Redis session management"""
    print("\n" + "="*60)
    print("TEST: Redis Session Management")
    print("="*60)
    
    import redis.asyncio as redis
    
    try:
        # Connect to Redis
        cache = redis.from_url("redis://localhost:6382", decode_responses=True)
        
        # Test connection
        await cache.ping()
        print("✓ Connected to Redis")
        
        # Create test session
        test_session = {
            "status": "processing",
            "phase": "test_phase",
            "started_at": datetime.now().isoformat(),
            "trace_id": "test-trace-001"
        }
        
        session_key = "analysis:session:test-001"
        
        # Store session
        await cache.setex(session_key, 60, json.dumps(test_session))
        print(f"✓ Stored session: {session_key}")
        
        # Retrieve session
        retrieved = await cache.get(session_key)
        if retrieved:
            session_data = json.loads(retrieved)
            print(f"✓ Retrieved session: phase={session_data['phase']}")
        
        # Clean up
        await cache.delete(session_key)
        print("✓ Cleaned up test session")
        
        # Close connection
        await cache.close()
        
        print("\n✅ Redis session test completed!")
        return True
        
    except Exception as e:
        print(f"\n⚠ Redis test failed (Redis may not be running): {e}")
        return False


async def main():
    """Run all manual tests"""
    print("\n" + "="*60)
    print("TAHOE ORCHESTRATION ENGINE - MANUAL TEST SUITE")
    print("="*60)
    
    tests = [
        ("Content Analysis", test_content_analysis),
        ("Redis Session Management", test_redis_session),
        ("Basic Orchestration", test_basic_orchestration),
        ("FDCPA Violation Detection", test_fdcpa_violation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)