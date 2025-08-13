#!/usr/bin/env python3
"""
Validation script for the specification system.
Validates all components are working correctly.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.specifications import SpecificationParser, SpecificationValidator
from src.core.composition import AgentCompositionService, UniversalAgentFactory
from src.services.configuration_version import ConfigurationVersionService


def main():
    """Run specification system validation."""
    print("=" * 60)
    print("SPECIFICATION SYSTEM VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Test 1: Parser initialization
    print("\n1. Testing Specification Parser...")
    try:
        parser = SpecificationParser()
        print("   ✅ Parser initialized successfully")
        results.append(("Parser", True))
    except Exception as e:
        print(f"   ❌ Parser failed: {e}")
        results.append(("Parser", False))
    
    # Test 2: Validator initialization
    print("\n2. Testing Specification Validator...")
    try:
        validator = SpecificationValidator()
        print("   ✅ Validator initialized successfully")
        results.append(("Validator", True))
    except Exception as e:
        print(f"   ❌ Validator failed: {e}")
        results.append(("Validator", False))
    
    # Test 3: Factory initialization
    print("\n3. Testing Universal Agent Factory...")
    try:
        factory = UniversalAgentFactory()
        print("   ✅ Factory initialized successfully")
        results.append(("Factory", True))
    except Exception as e:
        print(f"   ❌ Factory failed: {e}")
        results.append(("Factory", False))
    
    # Test 4: Composition Service
    print("\n4. Testing Agent Composition Service...")
    try:
        service = AgentCompositionService()
        print("   ✅ Composition service initialized successfully")
        results.append(("Composition Service", True))
    except Exception as e:
        print(f"   ❌ Composition service failed: {e}")
        results.append(("Composition Service", False))
    
    # Test 5: Version Tracking
    print("\n5. Testing Configuration Version Service...")
    try:
        version_service = ConfigurationVersionService()
        stats = version_service.get_statistics()
        print(f"   ✅ Version service initialized successfully")
        print(f"      Storage path: {stats['storage_path']}")
        results.append(("Version Service", True))
    except Exception as e:
        print(f"   ❌ Version service failed: {e}")
        results.append(("Version Service", False))
    
    # Test 6: Load specifications
    print("\n6. Testing Specification Loading...")
    try:
        agents = service.list_available_agents()
        workflows = service.list_available_workflows()
        tools = service.list_available_tools()
        models = service.list_available_models()
        
        print(f"   ✅ Found specifications:")
        print(f"      - Agents: {len(agents)}")
        print(f"      - Workflows: {len(workflows)}")
        print(f"      - Tools: {len(tools)}")
        print(f"      - Models: {len(models)}")
        results.append(("Specification Loading", True))
    except Exception as e:
        print(f"   ❌ Loading failed: {e}")
        results.append(("Specification Loading", False))
    
    # Test 7: Validate example specification
    print("\n7. Testing Specification Validation...")
    try:
        if agents:
            spec = parser.load_agent_spec(agents[0])
            validator.validate_agent_spec(spec)
            warnings = validator.check_adk_compliance(spec)
            
            print(f"   ✅ Validated: {spec['metadata']['name']}")
            if warnings:
                print(f"      ⚠️ ADK warnings: {len(warnings)}")
                for w in warnings[:2]:
                    print(f"         - {w[:60]}...")
            else:
                print(f"      ✅ No ADK compliance issues")
            results.append(("Validation", True))
        else:
            print("   ⚠️ No specifications to validate")
            results.append(("Validation", None))
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        results.append(("Validation", False))
    
    # Test 8: Agent composition
    print("\n8. Testing Agent Composition...")
    try:
        if agents:
            context = {
                "role": "test",
                "domain": "validation",
                "objective": "verify system"
            }
            agent = service.build_agent_from_spec(agents[0], context)
            print(f"   ✅ Built agent: {agent.name}")
            print(f"      Type: {type(agent).__name__}")
            results.append(("Agent Composition", True))
        else:
            print("   ⚠️ No agents to compose")
            results.append(("Agent Composition", None))
    except Exception as e:
        print(f"   ❌ Composition failed: {e}")
        results.append(("Agent Composition", False))
    
    # Test 9: Version tracking
    print("\n9. Testing Version Tracking...")
    try:
        if agents:
            spec = parser.load_agent_spec(agents[0])
            checksum = version_service.track_specification_version(spec)
            print(f"   ✅ Tracked version: {checksum[:8]}...")
            results.append(("Version Tracking", True))
        else:
            print("   ⚠️ No specifications to track")
            results.append(("Version Tracking", None))
    except Exception as e:
        print(f"   ❌ Version tracking failed: {e}")
        results.append(("Version Tracking", False))
    
    # Test 10: ADK Pattern Compliance
    print("\n10. Testing ADK Pattern Compliance...")
    try:
        # Test name sanitization
        test_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test-agent-with-hyphens"},
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }
        
        # Factory should sanitize the name
        agent = factory.build_agent(test_spec)
        if agent.name == "test_agent_with_hyphens":
            print("   ✅ Agent name sanitization works (hyphens → underscores)")
            results.append(("ADK Compliance", True))
        else:
            print(f"   ❌ Name not sanitized: {agent.name}")
            results.append(("ADK Compliance", False))
    except Exception as e:
        print(f"   ❌ ADK compliance test failed: {e}")
        results.append(("ADK Compliance", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️ SKIP"
        print(f"{status:10} {name}")
    
    print("\n" + "-" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n🎉 All critical components are working correctly!")
        return 0
    else:
        print("\n⚠️ Some components failed validation. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())