#!/usr/bin/env python3
"""Fix session_service() calls to use property instead."""

import os

# Files to fix
files = [
    "services/agent-engine/tests/test_adk_integration.py",
    "services/agent-engine/examples/basic_agent.py",
    "services/agent-engine/examples/tool_usage.py",
    "services/agent-engine/examples/workflow_agent.py"
]

def fix_file(filepath):
    """Fix session_service calls in a file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace session_service() with session_service
    new_content = content.replace("runner.session_service()", "runner.session_service")
    new_content = new_content.replace("session_service()", "session_service")
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"  ✓ Fixed session_service calls in {filepath}")
    else:
        print(f"  - No changes needed in {filepath}")

# Fix all files
for filepath in files:
    if os.path.exists(filepath):
        fix_file(filepath)
    else:
        print(f"  ✗ File not found: {filepath}")

print("\nDone!")