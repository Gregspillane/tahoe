#!/usr/bin/env python3
"""
Fix the 3 remaining critical issues in task files by creating corrected patterns.
This script generates the fixes that need to be applied to task files.
"""

import json
from pathlib import Path

def generate_fixes():
    """Generate the specific fixes needed for each issue."""
    
    fixes = {
        "circular_imports": {
            "description": "Fix circular import dependencies using dependency injection",
            "affected_tasks": [
                "r2-t01-agent-factory-base.yaml",
                "r2-t02-llm-agent-builder.yaml", 
                "r2-t03-workflow-agents.yaml",
                "r2-t04-custom-agents.yaml",
                "r2-t05-runner-integration.yaml"
            ],
            "fix_pattern": """
# BEFORE (Circular import):
from ..composition import UniversalAgentFactory

# AFTER (Dependency injection):
class LlmAgentBuilder(AgentBuilder):
    def __init__(self, tool_registry=None):
        self.instruction_builder = InstructionBuilder()
        self.tool_loader = ToolLoader(tool_registry)
        self.sub_agent_factory = None  # Will be set by factory
    
    def set_factory(self, factory):
        '''Set the factory reference for sub-agent creation.'''
        self.sub_agent_factory = factory
        return self

# In factory registration:
builder = LlmAgentBuilder()
builder.set_factory(self)
factory.register_builder("llm", builder)
"""
        },
        
        "session_patterns": {
            "description": "Fix session service access to use property pattern",
            "affected_tasks": [
                "r2-t05-runner-integration.yaml",
                "r4-t01-workflow-engine-base.yaml",
                "r4-t04-event-streaming.yaml",
                "r5-t01-session-orchestration.yaml",
                "r5-t02-multi-backend-support.yaml",
                "r5-t03-session-recovery.yaml"
            ],
            "fix_pattern": """
# BEFORE (Incorrect method call):
session_service = runner.session_service()
session = session_service.create_session(...)

# OR
session = runner.session_service().create_session(...)

# AFTER (Correct property access):
session_service = runner.session_service  # No parentheses - it's a property!
session = session_service.create_session(...)
"""
        },
        
        "agent_naming": {
            "description": "Add agent name validation for Python identifier compliance",
            "affected_tasks": [
                "r2-t01-agent-factory-base.yaml",
                "r2-t02-llm-agent-builder.yaml",
                "r2-t03-workflow-agents.yaml",
                "r2-t04-custom-agents.yaml"
            ],
            "fix_pattern": """
# Add this validation method to builders:
def validate_agent_name(self, name: str) -> str:
    '''Validate and fix agent name to be a valid Python identifier.'''
    import re
    
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
        logger.warning(f"Agent name '{name}' is not valid, using '{fixed_name}'")
    
    return fixed_name

# Use in agent creation:
agent = LlmAgent(
    name=self.validate_agent_name(metadata.get("name", "unnamed_agent")),
    # ... other parameters
)
"""
        }
    }
    
    return fixes

def create_fix_summary():
    """Create a summary of fixes to apply."""
    fixes = generate_fixes()
    
    print("="*70)
    print("TASK FILE FIXES - MANUAL APPLICATION GUIDE")
    print("="*70)
    print("\nThese fixes need to be applied to the task files to resolve critical issues.\n")
    
    for issue_key, issue_data in fixes.items():
        print(f"\n{'='*70}")
        print(f"ISSUE: {issue_data['description']}")
        print(f"{'='*70}")
        
        print(f"\nAffected tasks ({len(issue_data['affected_tasks'])}):")
        for task in issue_data['affected_tasks']:
            print(f"  - tasks/r2-composition/{task}" if "r2-" in task else f"  - tasks/{task.replace('-', '/', 1)}")
        
        print(f"\nFix Pattern:")
        print(issue_data['fix_pattern'])
    
    # Create a JSON file with the fixes for programmatic use
    fix_json = {
        "fixes": [
            {
                "issue": key,
                "description": data["description"],
                "affected_tasks": data["affected_tasks"],
                "pattern": data["fix_pattern"]
            }
            for key, data in fixes.items()
        ]
    }
    
    output_file = Path("/Users/gregspillane/Documents/Projects/tahoe/task_fixes.json")
    with open(output_file, 'w') as f:
        json.dump(fix_json, f, indent=2)
    
    print(f"\n{'='*70}")
    print("APPLICATION INSTRUCTIONS")
    print(f"{'='*70}")
    print("""
1. CIRCULAR IMPORTS (R2 tasks):
   - Add set_factory() method to each builder class
   - Remove direct factory imports
   - Use dependency injection pattern

2. SESSION PATTERNS (R4, R5 tasks):  
   - Change runner.session_service() to runner.session_service
   - Remove parentheses - it's a property, not a method

3. AGENT NAMING (R2 builder tasks):
   - Add validate_agent_name() method
   - Use it when creating agents
   - Ensures Python identifier compliance

Fix details saved to: task_fixes.json

These are content changes within the YAML files' 'content_structure' sections.
The YAML structure itself remains unchanged.
""")

if __name__ == "__main__":
    create_fix_summary()