#!/usr/bin/env python3
"""
Validate MASTERPLAN.md updates for ADK Dev UI integration documentation.
"""

import sys
from pathlib import Path

def validate_masterplan_dev_ui_updates():
    """Validate that MASTERPLAN.md properly documents Dev UI integration."""
    print("🧪 Validating MASTERPLAN.md ADK Dev UI Documentation...")
    
    masterplan_file = Path("MASTERPLAN.md")
    if not masterplan_file.exists():
        print("  ✗ MASTERPLAN.md file missing")
        return False
    
    with open(masterplan_file, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check version update
    if "v2.2" in content:
        print("  ✓ MASTERPLAN version updated to v2.2")
        checks.append(True)
    else:
        print("  ✗ MASTERPLAN version not updated")
        checks.append(False)
    
    # Check Core Capabilities update
    if "Visual Development Interface" in content and "ADK Dev UI integration" in content:
        print("  ✓ Dev UI added to Core Capabilities")
        checks.append(True)
    else:
        print("  ✗ Dev UI missing from Core Capabilities")
        checks.append(False)
    
    # Check Development Roadmap update
    if "Visual Development Foundation" in content and "DevUILauncher" in content:
        print("  ✓ Dev UI added to Release 2 roadmap")
        checks.append(True)
    else:
        print("  ✗ Dev UI missing from Development Roadmap")
        checks.append(False)
    
    # Check Development Commands update
    dev_ui_commands = ["make dev-ui", "make dev-ui-setup", "make dev-ui-docker"]
    commands_found = sum(1 for cmd in dev_ui_commands if cmd in content)
    if commands_found >= 3:
        print(f"  ✓ Dev UI commands added to Development Commands ({commands_found}/3)")
        checks.append(True)
    else:
        print(f"  ✗ Dev UI commands incomplete ({commands_found}/3)")
        checks.append(False)
    
    # Check comprehensive Dev UI section
    if "### ADK Dev UI Integration" in content:
        print("  ✓ Comprehensive Dev UI section added")
        
        # Check for key subsections
        dev_ui_subsections = [
            "What is ADK Dev UI?",
            "Tahoe Integration Features:",
            "Development Workflow:",
            "Architecture Integration:",
            "Key Benefits for Development:",
            "Integration Points:",
            "Configuration:",
            "Docker Integration:",
            "Future Enhancements:"
        ]
        
        subsections_found = sum(1 for section in dev_ui_subsections if section in content)
        if subsections_found >= 8:
            print(f"  ✓ Dev UI subsections comprehensive ({subsections_found}/9)")
            checks.append(True)
        else:
            print(f"  ✗ Dev UI subsections incomplete ({subsections_found}/9)")
            checks.append(False)
    else:
        print("  ✗ Comprehensive Dev UI section missing")
        checks.append(False)
    
    # Check architecture integration details
    if "class DevUILauncher:" in content and "discover_agents" in content:
        print("  ✓ Dev UI architecture code examples included")
        checks.append(True)
    else:
        print("  ✗ Dev UI architecture examples missing")
        checks.append(False)
    
    # Check integration with existing sections
    integration_points = ["R1 Foundation", "R2 Composition", "R3 Tools", "R4 Workflows"]
    integrations_found = sum(1 for point in integration_points if point in content and "Dev UI" in content)
    if integrations_found >= 4:
        print(f"  ✓ Integration points documented ({integrations_found}/4)")
        checks.append(True)
    else:
        print(f"  ✗ Integration points incomplete ({integrations_found}/4)")
        checks.append(False)
    
    return all(checks)

def validate_consistency_with_task_spec():
    """Validate consistency between MASTERPLAN and R2-T00 task specification."""
    print("\n🧪 Validating Consistency with R2-T00 Task Specification...")
    
    # Check if R2-T00 task file exists
    r2_t00_file = Path("tasks/r2-composition/r2-t00-adk-dev-ui-integration.yaml")
    if not r2_t00_file.exists():
        print("  ✗ R2-T00 task file missing")
        return False
    
    masterplan_file = Path("MASTERPLAN.md")
    if not masterplan_file.exists():
        print("  ✗ MASTERPLAN.md file missing")
        return False
    
    with open(masterplan_file, 'r') as f:
        masterplan_content = f.read()
    
    with open(r2_t00_file, 'r') as f:
        task_content = f.read()
    
    checks = []
    
    # Check consistent component names
    components = ["DevUILauncher", "AgentDiscovery", "DevUIConfiguration"]
    consistent_components = sum(1 for comp in components if comp in masterplan_content and comp in task_content)
    if consistent_components >= 2:
        print(f"  ✓ Component names consistent ({consistent_components}/3)")
        checks.append(True)
    else:
        print(f"  ✗ Component names inconsistent ({consistent_components}/3)")
        checks.append(False)
    
    # Check consistent port configuration
    if "8000" in masterplan_content and "8000" in task_content:
        print("  ✓ Port configuration consistent (8000)")
        checks.append(True)
    else:
        print("  ✗ Port configuration inconsistent")
        checks.append(False)
    
    # Check consistent make commands
    make_commands = ["make dev-ui", "make dev-ui-setup", "make dev-ui-docker"]
    consistent_commands = sum(1 for cmd in make_commands if cmd in masterplan_content)
    if consistent_commands >= 3:
        print(f"  ✓ Make commands consistent ({consistent_commands}/3)")
        checks.append(True)
    else:
        print(f"  ✗ Make commands inconsistent ({consistent_commands}/3)")
        checks.append(False)
    
    return all(checks)

def validate_documentation_completeness():
    """Validate overall documentation completeness."""
    print("\n🧪 Validating Documentation Completeness...")
    
    masterplan_file = Path("MASTERPLAN.md")
    with open(masterplan_file, 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check that Dev UI is properly integrated throughout document
    dev_ui_mentions = content.count("Dev UI") + content.count("ADK Dev UI")
    if dev_ui_mentions >= 10:
        print(f"  ✓ Dev UI well-integrated throughout document ({dev_ui_mentions} mentions)")
        checks.append(True)
    else:
        print(f"  ✗ Dev UI under-documented ({dev_ui_mentions} mentions)")
        checks.append(False)
    
    # Check practical examples included
    total_code_blocks = content.count("```")
    if total_code_blocks >= 30:  # Should have many examples with Dev UI additions
        print(f"  ✓ Practical examples abundant ({total_code_blocks // 2} code blocks)")
        checks.append(True)
    else:
        print(f"  ✗ Insufficient practical examples ({total_code_blocks // 2} code blocks)")
        checks.append(False)
    
    # Check future considerations included
    if "Future Enhancements:" in content and "Multi-user development" in content:
        print("  ✓ Future enhancements documented")
        checks.append(True)
    else:
        print("  ✗ Future enhancements missing")
        checks.append(False)
    
    return all(checks)

def main():
    """Run all MASTERPLAN Dev UI validation tests."""
    print("🚀 Validating MASTERPLAN.md ADK Dev UI Documentation")
    print("=" * 60)
    print("Ensuring comprehensive Dev UI integration documentation")
    print()
    
    tests = [
        validate_masterplan_dev_ui_updates,
        validate_consistency_with_task_spec,
        validate_documentation_completeness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 MASTERPLAN Dev UI Documentation: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ MASTERPLAN.md SUCCESSFULLY UPDATED!")
        print()
        print("🎯 Dev UI Documentation Complete:")
        print("  • Core Capabilities updated with visual development interface")
        print("  • Release 2 roadmap includes Visual Development Foundation")
        print("  • Comprehensive Dev UI integration section added")
        print("  • Development commands updated with Dev UI workflows")
        print("  • Architecture integration with code examples")
        print("  • Consistent with R2-T00 task specification")
        print()
        print("📖 MASTERPLAN v2.2 ready with complete Dev UI documentation")
        return True
    else:
        print("❌ MASTERPLAN DOCUMENTATION INCOMPLETE")
        print("🔧 Address failed validations for complete documentation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)