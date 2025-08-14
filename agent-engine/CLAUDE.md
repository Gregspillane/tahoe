
## Critical: ADK Documentation Requirements

### Context
**IMPORTANT: Google ADK was released after Claude's training cutoff** - Claude has zero inherent knowledge about Google ADK. Every technical decision MUST be validated against the official ADK documentation.

⚠️ **WARNING: Deviating from the official ADK documentation and attempting to build custom implementations will break the project. Always follow ADK patterns exactly as documented.**

### Documentation Structure

According to the ADK documentation found in `get-started/quickstart/` and `get-started/installation/`, the proper project structure is:

**Project Folder Structure:**
```
parent_folder/
    your_agent_name/
        __init__.py      # Contains: from . import agent
        agent.py         # Agent definition file
        .env            # API keys and configuration
```

### Core ADK Requirements

**According to `get-started/installation/` documentation:**

1. **Python Environment:**
   - Python 3.9+ required (Java 17+ for Java projects)
   - Virtual environment strongly recommended
   - Install via: `pip install google-adk`

2. **Model Configuration:**
   - Primary Model: `gemini-2.5-flash-lite` (as specified)
   - For streaming/voice: Must use models supporting Live API as documented in `get-started/streaming/quickstart-streaming/`

3. **Essential Imports (from `agents/llm-agents/` documentation):**
   ```python
   from google.adk.agents import Agent  # For basic agents
   from google.adk.agents import LlmAgent  # For LLM-powered agents
   from google.adk.tools import FunctionTool  # For custom tools
   ```

### Implementation Guidelines

**MANDATORY: Follow ADK Documentation Patterns**

As documented in `get-started/quickstart/`:
- Start with simple agent definitions
- Add tools incrementally
- Test each component before adding complexity
- Use ADK's built-in tools before creating custom ones

**FORBIDDEN: Custom Implementations Without Documentation**
- Never create custom architectures not shown in ADK docs
- Never modify ADK's internal components
- Never bypass ADK's tool creation patterns
- Never implement features not explicitly documented

### Documentation References

**Primary References:**
- Quick Start: `get-started/quickstart/`
- Installation: `get-started/installation/`
- Python API: `api-reference/python/`
- Agent Types: `agents/llm-agents/`, `agents/workflow-agents/`
- Tools: `tools/function-tools/`, `tools/built-in-tools/`

### Development Process

**Required Approach (from ADK documentation):**
1. **Start Simple:** Begin with basic agent from quickstart
2. **Validate Each Step:** Test functionality before proceeding
3. **Use Built-in Features:** Leverage ADK's provided tools and patterns
4. **Follow Examples:** Reference documented code examples exactly
5. **Incremental Complexity:** Add features one at a time

### Critical Reminders

✅ **DO:**
- Follow exact patterns from ADK documentation
- Use documented project structure
- Reference specific documentation sections
- Test incrementally
- Use ADK's built-in capabilities

❌ **DON'T:**
- Create custom architectures
- Skip documentation validation
- Combine patterns without documentation support
- Rush implementation
- Assume general software patterns apply to ADK

**Remember: The ADK documentation at `get-started/`, `agents/`, `tools/`, and `api-reference/` is the ONLY source of truth. Every implementation decision must be traceable to specific documentation.**

## Development Principles

### KISS (Keep It Simple, Stupid)
- Simple implementations over complex abstractions
- Minimal viable features first, iterate based on needs
- Clear, readable code over compact code
- Explicit over implicit - make intentions obvious

### Standards
- Fail fast with clear, actionable error messages
- Local environment should mirror production
- Prioritize code quality over backwards compatibility (pre-launch)

## Memory Bank System
- **Active context**: `/memory-bank/` - Living project documents
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions  
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log
- **Archived docs**: `/memory-bank/archive/` - Completed plans

