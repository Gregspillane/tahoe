#!/usr/bin/env python3
"""
Fix remaining critical issues in task files:
1. Circular import dependencies in R2 Composition
2. Session service access patterns
3. Agent naming validation
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def fix_circular_imports(filepath: Path) -> bool:
    """Fix circular import dependencies by using dependency injection pattern."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    changes_made = False
    
    # Fix 1: Remove direct factory imports from builders
    if 'from ..composition import UniversalAgentFactory' in content:
        content = content.replace(
            'from ..composition import UniversalAgentFactory',
            '# Factory will be injected via set_factory() method'
        )
        changes_made = True
    
    # Fix 2: Add factory injection pattern to builders
    if 'class LlmAgentBuilder(AgentBuilder):' in content or \
       'class SequentialAgentBuilder(AgentBuilder):' in content or \
       'class ParallelAgentBuilder(AgentBuilder):' in content:
        
        # Add set_factory method if not present
        if 'def set_factory(self, factory):' not in content:
            # Find the builder class and add the method
            pattern = r'(class \w+AgentBuilder\(AgentBuilder\):.*?\n.*?def __init__.*?\n(?:.*?\n)*?)(    def \w+)'
            replacement = r'\1    def set_factory(self, factory):\n        """Set the factory reference for sub-agent creation."""\n        self.sub_agent_factory = factory\n        return self\n    \n\2'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            changes_made = True
    
    # Fix 3: Update factory registration to inject factory reference
    if 'factory.register_builder' in content and 'set_factory' not in content:
        # Update registration pattern
        content = re.sub(
            r'factory\.register_builder\("(\w+)", (\w+)\(\)\)',
            r'factory.register_builder("\1", \2().set_factory(factory))',
            content
        )
        changes_made = True
    
    if changes_made:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def fix_session_service_patterns(filepath: Path) -> bool:
    """Fix session service access patterns to use property instead of method call."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    changes_made = False
    
    # Fix incorrect method call pattern
    if 'runner.session_service()' in content:
        # Replace method call with property access
        content = re.sub(
            r'runner\.session_service\(\)\.create_session',
            'runner.session_service.create_session',
            content
        )
        
        # Also fix standalone references
        content = re.sub(
            r'session_service = runner\.session_service\(\)',
            'session_service = runner.session_service',
            content
        )
        
        # Fix any chained calls
        content = re.sub(
            r'runner\.session_service\(\)\.',
            'runner.session_service.',
            content
        )
        changes_made = True
    
    # Fix session creation pattern
    incorrect_pattern = r'session = runner\.session_service\(\)\.create_session\('
    correct_pattern = 'session_service = runner.session_service\n            session = session_service.create_session('
    
    if re.search(incorrect_pattern, content):
        content = re.sub(incorrect_pattern, correct_pattern, content)
        changes_made = True
    
    if changes_made:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def add_agent_name_validation(filepath: Path) -> bool:
    """Add agent name validation to ensure Python identifier compliance."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    changes_made = False
    
    # Check if this is a builder file that needs validation
    if 'def validate_spec(self, spec: AgentSpec)' in content or \
       'def build(self, spec: AgentSpec' in content:
        
        # Add name validation if not present
        if 'isidentifier()' not in content and 'validate_agent_name' not in content:
            
            # Add validation helper function
            validation_helper = '''
              def validate_agent_name(self, name: str) -> str:
                  """Validate and fix agent name to be a valid Python identifier."""
                  # Replace hyphens and spaces with underscores
                  fixed_name = name.replace('-', '_').replace(' ', '_')
                  
                  # Remove any characters that aren't alphanumeric or underscore
                  fixed_name = re.sub(r'[^a-zA-Z0-9_]', '', fixed_name)
                  
                  # Ensure it doesn't start with a number
                  if fixed_name and fixed_name[0].isdigit():
                      fixed_name = f"agent_{fixed_name}"
                  
                  # Ensure it's not empty
                  if not fixed_name:
                      fixed_name = "unnamed_agent"
                  
                  # Validate it's a proper Python identifier
                  if not fixed_name.isidentifier():
                      logger.warning(f"Agent name '{name}' is not a valid Python identifier, using '{fixed_name}'")
                  
                  return fixed_name
'''
            
            # Find where to insert the helper
            if 'class ' in content and 'AgentBuilder' in content:
                # Insert after __init__ method
                pattern = r'(def __init__.*?\n(?:.*?\n)*?)(    def \w+)'
                replacement = validation_helper + r'\n\2'
                content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
                changes_made = True
            
            # Update build method to use validation
            if 'name=metadata.get("name"' in content:
                content = re.sub(
                    r'name=metadata\.get\("name", "unnamed_agent"\)',
                    'name=self.validate_agent_name(metadata.get("name", "unnamed_agent"))',
                    content
                )
                changes_made = True
            
            # Add import for re if needed
            if changes_made and 'import re' not in content:
                # Add re import after other imports
                content = re.sub(
                    r'(from typing import.*?\n)',
                    r'\1import re\n',
                    content
                )
    
    if changes_made:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def process_task_files():
    """Process all task files to fix remaining issues."""
    tasks_dir = Path('/Users/gregspillane/Documents/Projects/tahoe/tasks')
    
    # Track fixes
    fixes = {
        'circular_imports': [],
        'session_patterns': [],
        'agent_validation': []
    }
    
    # R2 Composition tasks - fix circular imports and agent validation
    r2_tasks = [
        'r2-composition/r2-t01-agent-factory-base.yaml',
        'r2-composition/r2-t02-llm-agent-builder.yaml',
        'r2-composition/r2-t03-workflow-agents.yaml',
        'r2-composition/r2-t04-custom-agents.yaml',
        'r2-composition/r2-t05-runner-integration.yaml'
    ]
    
    # Tasks needing session pattern fixes
    session_tasks = [
        'r2-composition/r2-t05-runner-integration.yaml',
        'r4-workflows/r4-t01-workflow-engine-base.yaml',
        'r4-workflows/r4-t04-event-streaming.yaml',
        'r5-sessions/r5-t01-session-orchestration.yaml',
        'r5-sessions/r5-t02-multi-backend-support.yaml',
        'r5-sessions/r5-t03-session-recovery.yaml'
    ]
    
    # Fix circular imports in R2 tasks
    print("Fixing circular import dependencies...")
    for task in r2_tasks:
        filepath = tasks_dir / task
        if filepath.exists():
            if fix_circular_imports(filepath):
                fixes['circular_imports'].append(task)
                print(f"  ✅ Fixed circular imports in {task}")
    
    # Fix session patterns
    print("\nFixing session service access patterns...")
    for task in session_tasks:
        filepath = tasks_dir / task
        if filepath.exists():
            if fix_session_service_patterns(filepath):
                fixes['session_patterns'].append(task)
                print(f"  ✅ Fixed session patterns in {task}")
    
    # Add agent name validation to builder tasks
    print("\nAdding agent name validation...")
    builder_tasks = r2_tasks[:4]  # First 4 R2 tasks are builders
    for task in builder_tasks:
        filepath = tasks_dir / task
        if filepath.exists():
            if add_agent_name_validation(filepath):
                fixes['agent_validation'].append(task)
                print(f"  ✅ Added name validation to {task}")
    
    # Summary
    print("\n" + "="*60)
    print("FIXES APPLIED SUMMARY")
    print("="*60)
    print(f"Circular imports fixed: {len(fixes['circular_imports'])} tasks")
    print(f"Session patterns fixed: {len(fixes['session_patterns'])} tasks")
    print(f"Agent validation added: {len(fixes['agent_validation'])} tasks")
    
    total_fixes = sum(len(v) for v in fixes.values())
    print(f"\nTotal fixes applied: {total_fixes}")
    
    # Verify fixes
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Check for remaining issues
    remaining_issues = []
    
    # Check for circular import patterns
    for task in r2_tasks:
        filepath = tasks_dir / task
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
                if 'from ..composition import UniversalAgentFactory' in content:
                    remaining_issues.append(f"{task}: Still has circular import")
    
    # Check for session patterns
    for task in session_tasks:
        filepath = tasks_dir / task
        if filepath.exists():
            with open(filepath, 'r') as f:
                content = f.read()
                if 'runner.session_service()' in content:
                    remaining_issues.append(f"{task}: Still has incorrect session pattern")
    
    if remaining_issues:
        print("⚠️ Remaining issues found:")
        for issue in remaining_issues:
            print(f"  - {issue}")
    else:
        print("✅ All critical issues have been fixed!")
        print("\nNext steps:")
        print("1. Review the changes in each task file")
        print("2. Run validation script to confirm all fixes")
        print("3. Proceed with implementation of R1, R3, and other valid tasks")

if __name__ == "__main__":
    print("Fixing Remaining Critical Issues in Task Files")
    print("="*60)
    process_task_files()