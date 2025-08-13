#!/usr/bin/env python3
"""
ADK Pattern Validation Script
Validates our implementation against official Google ADK documentation patterns
"""

import os
import sys
import json
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_imports() -> Tuple[bool, List[str]]:
    """Validate that all ADK imports follow documented patterns."""
    issues = []
    
    try:
        # Core agent imports
        from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
        
        # Verify Agent is alias for LlmAgent
        if Agent is not LlmAgent:
            issues.append("Agent should be an alias for LlmAgent")
        
        # Runner imports
        from google.adk.runners import InMemoryRunner
        
        # Session imports
        from google.adk.sessions import InMemorySessionService
        
        # Tool imports
        from google.adk.tools import FunctionTool, google_search
        
    except ImportError as e:
        issues.append(f"Import error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_agent_patterns() -> Tuple[bool, List[str]]:
    """Validate agent creation patterns match documentation."""
    issues = []
    
    try:
        from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
        
        # Test 1: LlmAgent basic creation
        llm_agent = LlmAgent(
            name="test_agent",
            model="gemini-2.0-flash",
            instruction="Test instruction"
        )
        
        # Create separate agents for each workflow to avoid parent conflict
        seq_sub = LlmAgent(
            name="seq_sub",
            model="gemini-2.0-flash",
            instruction="Sequential sub-agent"
        )
        
        par_sub = LlmAgent(
            name="par_sub",
            model="gemini-2.0-flash",
            instruction="Parallel sub-agent"
        )
        
        loop_sub = LlmAgent(
            name="loop_sub",
            model="gemini-2.0-flash",
            instruction="Loop sub-agent"
        )
        
        # Verify required attributes
        if not hasattr(llm_agent, 'name'):
            issues.append("LlmAgent missing 'name' attribute")
        if not hasattr(llm_agent, 'model'):
            issues.append("LlmAgent missing 'model' attribute")
        
        # Test 2: SequentialAgent with sub_agents
        seq_agent = SequentialAgent(
            name="test_sequential",
            sub_agents=[seq_sub],
            description="Test sequential"
        )
        
        if not hasattr(seq_agent, 'sub_agents'):
            issues.append("SequentialAgent missing 'sub_agents' attribute")
        
        # Test 3: ParallelAgent with sub_agents
        par_agent = ParallelAgent(
            name="test_parallel",
            sub_agents=[par_sub],
            description="Test parallel"
        )
        
        if not hasattr(par_agent, 'sub_agents'):
            issues.append("ParallelAgent missing 'sub_agents' attribute")
        
        # Test 4: LoopAgent with sub_agents (as list!)
        loop_agent = LoopAgent(
            name="test_loop",
            sub_agents=[loop_sub],  # Must be a list
            max_iterations=3,
            description="Test loop"
        )
        
        if not hasattr(loop_agent, 'sub_agents'):
            issues.append("LoopAgent missing 'sub_agents' attribute")
        if not hasattr(loop_agent, 'max_iterations'):
            issues.append("LoopAgent missing 'max_iterations' attribute")
        
    except Exception as e:
        issues.append(f"Agent pattern error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_runner_patterns() -> Tuple[bool, List[str]]:
    """Validate runner usage patterns."""
    issues = []
    
    try:
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import LlmAgent
        
        agent = LlmAgent(
            name="runner_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        
        # Test runner creation
        runner = InMemoryRunner(agent, app_name="test_app")
        
        # Verify runner attributes
        if not hasattr(runner, 'run'):
            issues.append("InMemoryRunner missing 'run' method")
        if not hasattr(runner, 'run_async'):
            issues.append("InMemoryRunner missing 'run_async' method")
        
        # Verify session service is a property, not a method
        if not hasattr(runner, 'session_service'):
            issues.append("InMemoryRunner missing 'session_service' property")
        else:
            # Access as property, not method call
            session_service = runner.session_service
            if session_service is None:
                issues.append("session_service property returned None")
        
    except Exception as e:
        issues.append(f"Runner pattern error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_session_patterns() -> Tuple[bool, List[str]]:
    """Validate session management patterns."""
    issues = []
    
    try:
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import LlmAgent
        import asyncio
        
        agent = LlmAgent(
            name="session_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        
        runner = InMemoryRunner(agent, app_name="test_app")
        session_service = runner.session_service  # Property, not method!
        
        # Check for sync or async session creation
        if hasattr(session_service, 'create_session_sync'):
            # Sync version available
            session = session_service.create_session_sync(
                app_name="test_app",
                user_id="test_user"
            )
        else:
            # Must use async
            async def create():
                return await session_service.create_session(
                    app_name="test_app",
                    user_id="test_user"
                )
            session = asyncio.run(create())
        
        # Verify session attributes
        if not hasattr(session, 'id'):
            issues.append("Session missing 'id' attribute")
        if not hasattr(session, 'app_name'):
            issues.append("Session missing 'app_name' attribute")
        if not hasattr(session, 'user_id'):
            issues.append("Session missing 'user_id' attribute")
        
    except Exception as e:
        issues.append(f"Session pattern error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_tool_patterns() -> Tuple[bool, List[str]]:
    """Validate tool integration patterns."""
    issues = []
    
    try:
        from google.adk.tools import FunctionTool, google_search
        from google.adk.agents import LlmAgent
        
        # Test automatic wrapping
        def simple_tool(x: int) -> int:
            return x * 2
        
        agent_auto = LlmAgent(
            name="auto_tool_test",
            model="gemini-2.0-flash",
            instruction="Test",
            tools=[simple_tool]  # Automatic wrapping
        )
        
        if not hasattr(agent_auto, 'tools'):
            issues.append("Agent missing 'tools' attribute with automatic wrapping")
        
        # Test explicit wrapping
        wrapped_tool = FunctionTool(simple_tool)
        
        agent_explicit = LlmAgent(
            name="explicit_tool_test",
            model="gemini-2.0-flash",
            instruction="Test",
            tools=[wrapped_tool]  # Explicit wrapping
        )
        
        if not hasattr(agent_explicit, 'tools'):
            issues.append("Agent missing 'tools' attribute with explicit wrapping")
        
        # Test built-in tool
        agent_builtin = LlmAgent(
            name="builtin_tool_test",
            model="gemini-2.0-flash",
            instruction="Test",
            tools=[google_search]  # Built-in tool
        )
        
        if not hasattr(agent_builtin, 'tools'):
            issues.append("Agent missing 'tools' attribute with built-in tool")
        
    except Exception as e:
        issues.append(f"Tool pattern error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_naming_conventions() -> Tuple[bool, List[str]]:
    """Validate agent naming conventions."""
    issues = []
    
    try:
        from google.adk.agents import LlmAgent
        
        # Test valid names (underscores)
        valid_names = ["test_agent", "my_assistant", "data_processor"]
        for name in valid_names:
            try:
                agent = LlmAgent(
                    name=name,
                    model="gemini-2.0-flash",
                    instruction="Test"
                )
            except Exception as e:
                issues.append(f"Valid name '{name}' rejected: {e}")
        
        # Test invalid names (hyphens should fail)
        invalid_names = ["test-agent", "my-assistant", "data-processor"]
        for name in invalid_names:
            try:
                agent = LlmAgent(
                    name=name,
                    model="gemini-2.0-flash",
                    instruction="Test"
                )
                issues.append(f"Invalid name '{name}' was accepted (should use underscores)")
            except Exception:
                # Expected to fail
                pass
        
    except Exception as e:
        issues.append(f"Naming convention error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def validate_parameter_patterns() -> Tuple[bool, List[str]]:
    """Validate parameter passing conventions."""
    issues = []
    
    try:
        from google.adk.agents import LlmAgent
        
        # Model parameters should NOT be in agent creation
        try:
            agent = LlmAgent(
                name="param_test",
                model="gemini-2.0-flash",
                instruction="Test",
                temperature=0.7,  # Should fail
                max_tokens=100    # Should fail
            )
            issues.append("Agent accepted temperature/max_tokens (should be runtime params)")
        except Exception:
            # Expected - these params should be set at runtime
            pass
        
        # Correct pattern - no model params in agent
        agent = LlmAgent(
            name="correct_param_test",
            model="gemini-2.0-flash",
            instruction="Test"
        )
        
    except Exception as e:
        issues.append(f"Parameter pattern error: {e}")
        return False, issues
    
    return len(issues) == 0, issues


def check_file_patterns(filepath: str) -> List[str]:
    """Check a Python file for ADK pattern violations."""
    issues = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for incorrect session service call
            if 'runner.session_service()' in line:
                issues.append(f"{filepath}:{i} - session_service is a property, not method")
            
            # Check for incorrect LoopAgent parameter
            if 'sub_agent=' in line and 'LoopAgent' in content and 'sub_agents' not in line:
                issues.append(f"{filepath}:{i} - LoopAgent uses 'sub_agents' (list), not 'sub_agent'")
            
            # Check for agent names with hyphens
            if 'name="' in line or "name='" in line:
                import re
                matches = re.findall(r'name=["\']([^"\']+)["\']', line)
                for name in matches:
                    if '-' in name and '_' not in name:
                        issues.append(f"{filepath}:{i} - Agent name '{name}' uses hyphens (should use underscores)")
            
            # Check for incorrect model parameters
            if 'LlmAgent(' in line:
                if 'temperature=' in line or 'max_tokens=' in line or 'top_p=' in line:
                    issues.append(f"{filepath}:{i} - Model parameters should be set at runtime, not in agent creation")
    
    except Exception as e:
        issues.append(f"Error checking {filepath}: {e}")
    
    return issues


def validate_project_files() -> Tuple[bool, List[str]]:
    """Validate all project Python files for ADK patterns."""
    all_issues = []
    
    # Define directories to check
    dirs_to_check = [
        "src",
        "scripts", 
        "tests",
        "examples"
    ]
    
    base_path = Path("/Users/gregspillane/Documents/Projects/tahoe/services/agent-engine")
    
    for dir_name in dirs_to_check:
        dir_path = base_path / dir_name
        if dir_path.exists():
            for py_file in dir_path.glob("**/*.py"):
                issues = check_file_patterns(str(py_file))
                if issues:
                    all_issues.extend(issues)
    
    return len(all_issues) == 0, all_issues


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("ADK PATTERN VALIDATION")
    print("=" * 70)
    print("\nValidating implementation against Google ADK documentation patterns...\n")
    
    results = {}
    all_issues = []
    
    # Run validation checks
    checks = [
        ("Import Patterns", validate_imports),
        ("Agent Creation Patterns", validate_agent_patterns),
        ("Runner Usage Patterns", validate_runner_patterns),
        ("Session Management Patterns", validate_session_patterns),
        ("Tool Integration Patterns", validate_tool_patterns),
        ("Naming Conventions", validate_naming_conventions),
        ("Parameter Passing Patterns", validate_parameter_patterns),
        ("Project File Patterns", validate_project_files)
    ]
    
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        success, issues = check_func()
        results[check_name] = success
        
        if success:
            print(f"  ✓ {check_name} validated successfully")
        else:
            print(f"  ✗ {check_name} has issues:")
            for issue in issues:
                print(f"    - {issue}")
                all_issues.append(f"{check_name}: {issue}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if all_issues:
        print(f"\nTotal issues found: {len(all_issues)}")
        print("\nIssues to address:")
        for issue in all_issues:
            print(f"  • {issue}")
    else:
        print("\n✓ All ADK patterns validated successfully!")
        print("  Your implementation follows Google ADK documentation patterns.")
    
    # Save validation report
    report = {
        "validation_date": str(Path(__file__).stat().st_mtime),
        "checks_passed": passed,
        "checks_total": total,
        "success": len(all_issues) == 0,
        "results": results,
        "issues": all_issues
    }
    
    report_path = Path(__file__).parent / "adk_validation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nValidation report saved to: {report_path}")
    
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)