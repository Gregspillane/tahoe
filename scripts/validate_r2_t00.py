#!/usr/bin/env python3
"""
Validate R2-T00: ADK Dev UI Integration task specification.
"""

import sys
import yaml
from pathlib import Path

def validate_r2_t00_specification():
    """Validate R2-T00 task specification structure and content."""
    print("🧪 Validating R2-T00: ADK Dev UI Integration Task Specification...")
    
    # Load R2-T00 task file
    task_file = Path("tasks/r2-composition/r2-t00-adk-dev-ui-integration.yaml")
    if not task_file.exists():
        print("  ✗ R2-T00 task file missing")
        return False
    
    try:
        with open(task_file) as f:
            task_spec = yaml.safe_load(f)
    except Exception as e:
        print(f"  ✗ Failed to parse R2-T00 YAML: {e}")
        return False
    
    checks = []
    
    # Check basic structure
    if "metadata" in task_spec:
        metadata = task_spec["metadata"]
        if metadata.get("name") == "r2-t00-adk-dev-ui-integration":
            print("  ✓ Task name correct")
            checks.append(True)
        else:
            print(f"  ✗ Task name incorrect: {metadata.get('name')}")
            checks.append(False)
            
        if "adk" in metadata.get("tags", []):
            print("  ✓ ADK tag present")
            checks.append(True)
        else:
            print("  ✗ Missing ADK tag")
            checks.append(False)
    else:
        print("  ✗ Missing metadata section")
        checks.append(False)
    
    # Check spec structure
    if "spec" in task_spec:
        spec = task_spec["spec"]
        
        if spec.get("task_number") == "R2-T00":
            print("  ✓ Task number correct")
            checks.append(True)
        else:
            print(f"  ✗ Task number incorrect: {spec.get('task_number')}")
            checks.append(False)
            
        if spec.get("phase") == "R2 Composition":
            print("  ✓ Phase correct")
            checks.append(True)
        else:
            print(f"  ✗ Phase incorrect: {spec.get('phase')}")
            checks.append(False)
            
        # Check objectives
        if "objectives" in spec:
            objectives = spec["objectives"]
            primary_objectives = objectives.get("primary", [])
            if len(primary_objectives) >= 3:
                print(f"  ✓ Primary objectives defined ({len(primary_objectives)})")
                checks.append(True)
            else:
                print(f"  ✗ Insufficient primary objectives: {len(primary_objectives)}")
                checks.append(False)
        else:
            print("  ✗ Missing objectives section")
            checks.append(False)
    else:
        print("  ✗ Missing spec section")
        checks.append(False)
    
    # Check implementation details
    if "implementation" in task_spec.get("spec", {}):
        implementation = task_spec["spec"]["implementation"]
        
        if "architecture" in implementation:
            arch = implementation["architecture"]
            components = arch.get("components", [])
            if len(components) >= 4:
                print(f"  ✓ Architecture components defined ({len(components)})")
                checks.append(True)
            else:
                print(f"  ✗ Insufficient architecture components: {len(components)}")
                checks.append(False)
        else:
            print("  ✗ Missing architecture section")
            checks.append(False)
            
        if "detailed_implementation" in implementation:
            detailed = implementation["detailed_implementation"]
            steps = [k for k in detailed.keys() if k.startswith("step_")]
            if len(steps) >= 6:
                print(f"  ✓ Implementation steps defined ({len(steps)})")
                checks.append(True)
            else:
                print(f"  ✗ Insufficient implementation steps: {len(steps)}")
                checks.append(False)
        else:
            # Check if detailed_implementation is at spec level
            if "detailed_implementation" in task_spec.get("spec", {}):
                detailed = task_spec["spec"]["detailed_implementation"]
                steps = [k for k in detailed.keys() if k.startswith("step_")]
                if len(steps) >= 6:
                    print(f"  ✓ Implementation steps defined ({len(steps)})")
                    checks.append(True)
                else:
                    print(f"  ✗ Insufficient implementation steps: {len(steps)}")
                    checks.append(False)
            else:
                print("  ✗ Missing detailed implementation")
                checks.append(False)
    else:
        print("  ✗ Missing implementation section")
        checks.append(False)
    
    # Check validation criteria
    if "validation" in task_spec.get("spec", {}):
        validation = task_spec["spec"]["validation"]
        
        success_criteria = validation.get("success_criteria", [])
        if len(success_criteria) >= 5:
            print(f"  ✓ Success criteria defined ({len(success_criteria)})")
            checks.append(True)
        else:
            print(f"  ✗ Insufficient success criteria: {len(success_criteria)}")
            checks.append(False)
            
        test_cases = validation.get("test_cases", [])
        if len(test_cases) >= 4:
            print(f"  ✓ Test cases defined ({len(test_cases)})")
            checks.append(True)
        else:
            print(f"  ✗ Insufficient test cases: {len(test_cases)}")
            checks.append(False)
    else:
        print("  ✗ Missing validation section")
        checks.append(False)
    
    return all(checks)

def validate_dependency_updates():
    """Validate that R2-T01 and R2-T02 dependencies include R2-T00."""
    print("\n🧪 Validating R2 Task Dependencies...")
    
    checks = []
    
    # Check R2-T01 dependencies
    r2_t01_file = Path("tasks/r2-composition/r2-t01-agent-factory-base.yaml")
    if r2_t01_file.exists():
        try:
            with open(r2_t01_file) as f:
                content = f.read()
            
            if "r2-t00-adk-dev-ui-integration" in content:
                print("  ✓ R2-T01 includes R2-T00 dependency")
                checks.append(True)
            else:
                print("  ✗ R2-T01 missing R2-T00 dependency")
                checks.append(False)
        except Exception as e:
            print(f"  ✗ Error reading R2-T01: {e}")
            checks.append(False)
    else:
        print("  ✗ R2-T01 task file missing")
        checks.append(False)
    
    # Check R2-T02 dependencies  
    r2_t02_file = Path("tasks/r2-composition/r2-t02-llm-agent-builder.yaml")
    if r2_t02_file.exists():
        try:
            with open(r2_t02_file) as f:
                content = f.read()
            
            if "r2-t00-adk-dev-ui-integration" in content:
                print("  ✓ R2-T02 includes R2-T00 dependency")
                checks.append(True)
            else:
                print("  ✗ R2-T02 missing R2-T00 dependency")
                checks.append(False)
        except Exception as e:
            print(f"  ✗ Error reading R2-T02: {e}")
            checks.append(False)
    else:
        print("  ✗ R2-T02 task file missing")
        checks.append(False)
    
    return all(checks)

def validate_task_structure():
    """Validate overall task structure and readiness."""
    print("\n🧪 Validating Task Structure...")
    
    checks = []
    
    # Check R2 composition directory
    r2_dir = Path("tasks/r2-composition")
    if r2_dir.exists():
        print("  ✓ R2 composition directory exists")
        checks.append(True)
        
        # Count R2 task files
        r2_tasks = list(r2_dir.glob("r2-t*.yaml"))
        if len(r2_tasks) >= 7:  # R2-T00 through R2-T06
            print(f"  ✓ R2 task files present ({len(r2_tasks)})")
            checks.append(True)
        else:
            print(f"  ✗ Insufficient R2 task files: {len(r2_tasks)}")
            checks.append(False)
    else:
        print("  ✗ R2 composition directory missing")
        checks.append(False)
    
    # Check if R2-T00 is properly positioned
    r2_t00_file = Path("tasks/r2-composition/r2-t00-adk-dev-ui-integration.yaml")
    if r2_t00_file.exists():
        print("  ✓ R2-T00 properly positioned in R2 composition")
        checks.append(True)
    else:
        print("  ✗ R2-T00 not in correct location")
        checks.append(False)
    
    return all(checks)

def main():
    """Run all R2-T00 validations."""
    print("🚀 Validating R2-T00: ADK Dev UI Integration")
    print("=" * 60)
    print("Ensuring proper task specification and dependency setup")
    print()
    
    tests = [
        validate_r2_t00_specification,
        validate_dependency_updates,
        validate_task_structure
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
    print(f"📊 R2-T00 Validation: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ R2-T00 SPECIFICATION READY!")
        print()
        print("🎯 R2-T00 Key Features:")
        print("  • Comprehensive ADK Dev UI integration specification")
        print("  • 8-step detailed implementation plan") 
        print("  • Complete validation criteria and test cases")
        print("  • Proper dependency integration with R2 tasks")
        print("  • Foundation for visual agent development workflow")
        print()
        print("🚀 Ready to implement R2-T00 before proceeding to R2-T01")
        return True
    else:
        print("❌ R2-T00 SPECIFICATION NEEDS FIXES")
        print("🔧 Address failed validations before implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)