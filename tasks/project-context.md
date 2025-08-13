# Project Tahoe - Universal Agent Engine Context

## Architecture Overview
Universal agent orchestration platform using Google ADK for dynamic agent composition from specifications.

## Key Architectural Decisions

1. **Specification-Driven**: All agents defined in YAML/JSON, not code
2. **Universal Factory**: Single factory creates all agent types
3. **Plugin Architecture**: Runtime tool registration
4. **Multi-Backend Sessions**: Memory, Redis, Vertex support
5. **ADK-Native**: Use framework capabilities, don't reinvent

## ADK Components Used

### Core Agents
- **LlmAgent** (aliased as Agent): Primary LLM-based agent
- **SequentialAgent**: Sequential workflow execution
- **ParallelAgent**: Parallel execution of sub-agents
- **LoopAgent**: Iterative execution patterns
- **BaseAgent**: Base class for custom agents

### Runtime Components
- **InMemoryRunner**: Primary execution runtime
  - `run()`: Synchronous execution
  - `run_async()`: Asynchronous streaming execution
- **Session Services**:
  - `InMemorySessionService`: Default in-memory sessions
  - Custom backends for Redis and Vertex

### Tools
- **FunctionTool**: Explicit tool wrapping when needed
- **Automatic wrapping**: Most functions work without explicit wrapping
- **Built-in tools**: google_search and others

## Specification Standards

### Version
- Current: `agent-engine/v1`
- Location: `specs/{agents,workflows,tools,models}/`
- Format: YAML with JSON Schema validation

### Required Fields
All specifications must include:
- `apiVersion`: Version of specification format
- `kind`: Type of specification (AgentSpec, WorkflowTemplate, ToolSpec, ModelConfig)
- `metadata`: Name, version, description, tags
- `spec`: Actual specification content

### Agent Types
- `llm`: LLM-based agent (LlmAgent)
- `sequential`: Sequential workflow (SequentialAgent)
- `parallel`: Parallel execution (ParallelAgent)
- `loop`: Iterative patterns (LoopAgent)
- `custom`: Custom implementation (BaseAgent)

## Established Patterns

### Agent Creation Pattern
```python
# Universal factory pattern
factory = UniversalAgentFactory()
agent = factory.build_agent(spec_name="analyzer", context={"role": "analyst"})
```

### Tool Registration Pattern
```python
# Runtime tool registration
registry = ToolRegistry()
registry.register_tool(tool_spec)
tools = registry.get_tools_for_agent(["tool1", "tool2"])
```

### Workflow Execution Pattern
```python
# Template-driven workflows
engine = WorkflowEngine()
result = await engine.execute_workflow("parallel-analysis", input_data, session_id)
```

### Session Management Pattern
```python
# Multi-backend sessions
orchestrator = SessionOrchestrator()
session_id = orchestrator.create_session({
    "persistence": "redis",
    "app_name": "agent-engine",
    "user_id": "user123"
})
```

## Interface Contracts

### Agent Factory Interface
- `build_agent(spec_name: str, context: dict = None) -> BaseAgent`
- `load_agent_spec(spec_name: str) -> dict`
- `validate_spec(spec: dict) -> bool`

### Tool Registry Interface
- `register_tool(tool_spec: dict) -> bool`
- `get_tool(name: str) -> callable`
- `get_tools_for_agent(tool_names: list) -> list`
- `validate_tool(tool_spec: dict) -> bool`

### Workflow Engine Interface
- `execute_workflow(template_name: str, input_data: dict, session_id: str) -> dict`
- `load_workflow_template(template_name: str) -> dict`
- `validate_template(template: dict) -> bool`

### Session Orchestrator Interface
- `create_session(config: dict) -> str`
- `get_session(session_id: str) -> Session`
- `update_session_state(session_id: str, state: dict) -> bool`
- `fork_session(session_id: str) -> str`

## Configuration Management

### Environment Variables
```
# Shared Infrastructure
DATABASE_HOST=localhost
DATABASE_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379

# Service-Specific
AGENT_ENGINE_PORT=8001
AGENT_ENGINE_LOG_LEVEL=INFO
AGENT_ENGINE_DB_SCHEMA=agent_engine
AGENT_ENGINE_REDIS_NAMESPACE=agent:

# ADK Model Configuration
GEMINI_API_KEY=your-gemini-key
ADK_DEFAULT_MODEL=gemini-2.0-flash
ADK_TEMPERATURE=0.2
ADK_MAX_TOKENS=8192
ADK_SESSION_SERVICE=memory
```

### Configuration Hierarchy
1. Base `.env` file
2. Environment-specific overrides (`config/{environment}.env`)
3. Runtime specifications

## Testing Standards

### Coverage Requirements
- Unit tests: 85% minimum coverage
- Integration tests: All ADK integrations
- E2E tests: Complete user scenarios
- Performance tests: Sub-500ms API responses

### Test Organization
- `tests/unit/`: Component tests
- `tests/integration/`: ADK integration tests
- `tests/e2e/`: End-to-end scenarios
- `tests/fixtures/`: Test data and specs

## Development Workflow

### Local Development
```bash
# Install dependencies
pip install google-adk
pip install -r requirements.txt

# Set up environment
export GEMINI_API_KEY="your-key"

# Run application
uvicorn main:app --reload --port 8001

# Run tests
pytest tests/ -v --cov=src
```

### Docker Development
```bash
# Build and run
docker-compose up agent-engine

# Run tests in container
docker-compose run agent-engine pytest tests/
```

## Task Completion Tracking

### R1 - Foundation
- [ ] r1-t01: Project setup
- [ ] r1-t02: ADK verification
- [ ] r1-t03: Specification system
- [ ] r1-t04: Database setup
- [ ] r1-t05: Configuration loader

### R2 - Composition
- [ ] r2-t01: Agent factory base
- [ ] r2-t02: LLM agent builder
- [ ] r2-t03: Workflow agents
- [ ] r2-t04: Custom agents
- [ ] r2-t05: Runner integration
- [ ] r2-t06: Composition tests

### R3 - Tools
- [ ] r3-t01: Tool registry
- [ ] r3-t02: Tool loading
- [ ] r3-t03: Built-in tools
- [ ] r3-t04: Tool collections

### R4 - Workflows
- [ ] r4-t01: Template system
- [ ] r4-t02: Workflow engine
- [ ] r4-t03: Conditional workflows
- [ ] r4-t04: Workflow testing
- [ ] r4-t05: Workflow examples

### R5 - Sessions
- [ ] r5-t01: Session orchestrator
- [ ] r5-t02: Memory backend
- [ ] r5-t03: Redis backend
- [ ] r5-t04: Session testing

### R6 - API
- [ ] r6-t01: Core endpoints
- [ ] r6-t02: Agent endpoints
- [ ] r6-t03: Workflow endpoints
- [ ] r6-t04: Tool endpoints
- [ ] r6-t05: API testing

### R7 - Integration
- [ ] r7-t01: System integration
- [ ] r7-t02: E2E testing
- [ ] r7-t03: Performance testing
- [ ] r7-t04: Deployment prep

## Notes for Future Sessions

### Critical Reminders
- Always use ADK components, don't reinvent
- Specifications drive everything
- Tools are plugins, not hardcoded
- Sessions can use different backends
- Models are configurable with fallbacks

### Common Pitfalls to Avoid
- Don't implement custom retry logic (ADK provides)
- Don't manage sessions manually (use ADK services)
- Don't hardcode business logic
- Don't create custom agent base classes (use BaseAgent)
- Don't wrap functions unnecessarily (ADK handles most)

### Key Success Factors
- Follow ADK documentation exactly
- Test with real ADK components early
- Use specifications for all configuration
- Keep the system universal and domain-agnostic
- Maintain clear separation of concerns