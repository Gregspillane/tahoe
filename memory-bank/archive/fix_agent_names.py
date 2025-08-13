#!/usr/bin/env python3
"""Fix agent names to use underscores instead of hyphens."""

import re
import os

# Files to fix
files = [
    "services/agent-engine/tests/test_adk_integration.py",
    "services/agent-engine/examples/basic_agent.py",
    "services/agent-engine/examples/tool_usage.py",
    "services/agent-engine/examples/workflow_agent.py"
]

# Pattern to find agent names with hyphens
pattern = r'name="([a-zA-Z0-9]+)-([a-zA-Z0-9-]+)"'

def fix_file(filepath):
    """Fix agent names in a file."""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all matches
    matches = re.findall(pattern, content)
    
    # Replace hyphens with underscores in agent names
    def replace_name(match):
        full_match = match.group(0)
        name_part = match.group(0)[6:-1]  # Extract the name between quotes
        fixed_name = name_part.replace('-', '_')
        return f'name="{fixed_name}"'
    
    new_content = re.sub(pattern, replace_name, content)
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"  ✓ Fixed agent names in {filepath}")
    else:
        print(f"  - No changes needed in {filepath}")

# Fix all files
for filepath in files:
    if os.path.exists(filepath):
        fix_file(filepath)
    else:
        print(f"  ✗ File not found: {filepath}")

print("\nDone!")