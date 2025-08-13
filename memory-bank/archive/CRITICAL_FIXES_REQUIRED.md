# Critical Fixes Required for Task Files

## Summary
There are 3 critical issues preventing 15 task files from being implementation-ready. These fixes are required before proceeding with R2, R4, and R5 implementation.

## Issue 1: Circular Import Dependencies ❌

### Affected Tasks (5):
- `r2-t01-agent-factory-base.yaml`
- `r2-t02-llm-agent-builder.yaml`
- `r2-t03-workflow-agents.yaml`
- `r2-t04-custom-agents.yaml`
- `r2-t05-runner-integration.yaml`

### Problem:
Builders try to import the factory, and factory imports builders = circular dependency

### Solution:
Use dependency injection pattern - builders don't import factory, factory injects itself

### Required Changes:

#### In each builder class (r2-t02, r2-t03, r2-t04):
```python
# REMOVE this line:
from ..composition import UniversalAgentFactory

# ADD this method to builder classes:
def set_factory(self, factory):
    """Set the factory reference for sub-agent creation."""
    self.sub_agent_factory = factory
    return self
```

#### In factory registration (r2-t01):
```python
# Change from:
factory.register_builder("llm", LlmAgentBuilder())

# To:
builder = LlmAgentBuilder()
builder.set_factory(factory)
factory.register_builder("llm", builder)
```

## Issue 2: Session Service Access Pattern ❌

### Affected Tasks (6):
- `r2-t05-runner-integration.yaml`
- `r4-t01-workflow-engine-base.yaml`
- `r4-t04-event-streaming.yaml`
- `r5-t01-session-orchestration.yaml`
- `r5-t02-multi-backend-support.yaml`
- `r5-t03-session-recovery.yaml`

### Problem:
Tasks incorrectly call `runner.session_service()` as a method instead of accessing it as a property

### Solution:
Remove parentheses - it's a property, not a method

### Required Changes:
```python
# WRONG - causes AttributeError:
session_service = runner.session_service()
session = runner.session_service().create_session(...)

# CORRECT - property access:
session_service = runner.session_service  # No parentheses!
session = session_service.create_session(...)
```

## Issue 3: Agent Name Validation ❌

### Affected Tasks (4):
- `r2-t01-agent-factory-base.yaml`
- `r2-t02-llm-agent-builder.yaml`
- `r2-t03-workflow-agents.yaml`
- `r2-t04-custom-agents.yaml`

### Problem:
Agent names with hyphens or special characters cause Python identifier errors

### Solution:
Add validation method to ensure names are valid Python identifiers

### Required Changes:

Add this method to each builder class:
```python
def validate_agent_name(self, name: str) -> str:
    """Validate and fix agent name to be a valid Python identifier."""
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
    
    # Log if name was changed
    if fixed_name != name:
        logger.warning(f"Agent name '{name}' changed to '{fixed_name}' for Python compliance")
    
    return fixed_name
```

Use in agent creation:
```python
# Change from:
name=metadata.get("name", "unnamed_agent")

# To:
name=self.validate_agent_name(metadata.get("name", "unnamed_agent"))
```

## Implementation Priority

### Phase 1: Fix R2 Composition Tasks (Highest Priority)
These are blocking many other tasks:
1. Fix circular imports in all 5 R2 tasks
2. Add agent name validation to 4 R2 builder tasks
3. Fix session pattern in r2-t05

### Phase 2: Fix R4 and R5 Tasks
Once R2 is fixed:
1. Fix session patterns in r4-t01 and r4-t04
2. Fix session patterns in r5-t01, r5-t02, r5-t03

## Verification

After applying fixes, verify:

1. **No circular imports**:
   ```python
   # Should work without import errors:
   from src.core.composition import UniversalAgentFactory
   from src.core.builders.llm_builder import LlmAgentBuilder
   ```

2. **Session access works**:
   ```python
   runner = InMemoryRunner(agent)
   session_service = runner.session_service  # No error
   session = session_service.create_session(...)
   ```

3. **Agent names validated**:
   ```python
   # "my-agent-name" becomes "my_agent_name"
   # "123agent" becomes "agent_123agent"
   # Works without identifier errors
   ```

## Time Estimate

- **Circular import fixes**: 2-3 hours
- **Session pattern fixes**: 1-2 hours  
- **Agent name validation**: 1-2 hours
- **Total**: 4-7 hours

## Notes

- These are changes to the Python code snippets within the YAML task files
- The YAML structure itself doesn't change
- All fixes follow validated ADK patterns from r1-t02
- Once fixed, 18/33 tasks (55%) will be ready for implementation