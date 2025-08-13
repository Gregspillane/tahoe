# Claude Code Task Generator for Project Tahoe - Universal Agent Engine

## Your Mission
Read the Project Tahoe masterplan (@MASTERPLAN.md) and create a complete task structure in the repository that breaks down the universal agent orchestration platform into executable sessions. Generate YAML task files that future Claude Code sessions can use to build the system autonomously.

## What You Will Create

### Directory Structure to Generate
```
tasks/
├── releases.yaml                    # Master release plan with all tracks
├── project-context.md              # Persistent context across all tasks
├── adk-patterns.md                 # ADK best practices reference
├── r1-foundation/
│   ├── r1-t01-project-setup.yaml
│   ├── r1-t02-adk-verification.yaml
│   ├── r1-t03-specification-system.yaml
│   ├── r1-t04-database-setup.yaml
│   └── r1-t05-configuration-loader.yaml
├── r2-composition/
│   ├── r2-t01-agent-factory-base.yaml
│   ├── r2-t02-llm-agent-builder.yaml
│   ├── r2-t03-workflow-agents.yaml
│   ├── r2-t04-custom-agents.yaml
│   ├── r2-t05-runner-integration.yaml
│   └── r2-t06-composition-tests.yaml
├── r3-tools/
│   ├── r3-t01-tool-registry.yaml
│   ├── r3-t02-tool-loading.yaml
│   ├── r3-t03-builtin-tools.yaml
│   └── r3-t04-tool-collections.yaml
├── r4-workflows/
│   ├── r4-t01-template-system.yaml
│   ├── r4-t02-workflow-engine.yaml
│   ├── r4-t03-conditional-workflows.yaml
│   ├── r4-t04-workflow-testing.yaml
│   └── r4-t05-workflow-examples.yaml
├── r5-sessions/
│   ├── r5-t01-session-orchestrator.yaml
│   ├── r5-t02-memory-backend.yaml
│   ├── r5-t03-redis-backend.yaml
│   └── r5-t04-session-testing.yaml
├── r6-api/
│   ├── r6-t01-core-endpoints.yaml
│   ├── r6-t02-agent-endpoints.yaml
│   ├── r6-t03-workflow-endpoints.yaml
│   ├── r6-t04-tool-endpoints.yaml
│   └── r6-t05-api-testing.yaml
├── r7-integration/
│   ├── r7-t01-system-integration.yaml
│   ├── r7-t02-e2e-testing.yaml
│   ├── r7-t03-performance-testing.yaml
│   └── r7-t04-deployment-prep.yaml
└── validation/
    ├── validate-tasks.py           # Script to validate all task files
    └── task-dependencies.md        # Dependency graph visualization
```

## File Templates to Use

### releases.yaml Template
```yaml
project:
  name: "tahoe-agent-engine"
  description: "Universal agent orchestration platform using Google ADK for dynamic agent composition"
  architecture: "Specification-driven with plugin-based tools and multi-backend sessions"
  adk_version: "google-adk (latest)"
  
releases:
  - id: "r1-foundation"
    name: "Foundation Infrastructure"
    description: "Core project setup with ADK integration and specification system"
    builds: "Basic infrastructure with ADK verification and specification parsing"
    tasks: ["r1-t01", "r1-t02", "r1-t03", "r1-t04", "r1-t05"]
    working_functionality:
      - "ADK imports and basic agent creation works"
      - "Specifications parse and validate"
      - "Database connected with Prisma"
      - "Configuration system operational"
    validates_with: |
      docker-compose up -d
      python -c "from google.adk.agents import LlmAgent; print('ADK OK')"
      curl localhost:8001/health
      pytest tests/test_specifications.py
    
  - id: "r2-composition"
    name: "Universal Agent Composition"
    description: "Dynamic agent factory supporting all ADK agent types"
    builds: "Complete agent composition engine from specifications"
    requires: ["r1-foundation"]
    tasks: ["r2-t01", "r2-t02", "r2-t03", "r2-t04", "r2-t05", "r2-t06"]
    working_functionality:
      - "LlmAgent creation from specifications"
      - "SequentialAgent, ParallelAgent, LoopAgent builders"
      - "Custom agent support via BaseAgent"
      - "InMemoryRunner integration"
    validates_with: |
      python tests/test_agent_factory.py
      curl -X POST localhost:8001/agents/compose -d @specs/agents/examples/analyzer.yaml
      python examples/create_workflow_agent.py

  # ... continue for r3-tools, r4-workflows, r5-sessions, r6-api, r7-integration
```

### Individual Task File Template
```yaml
task:
  id: "rX-tYY-descriptive-name"
  name: "Build <specific component>"
  description: "One-sentence description of what this task accomplishes"
  complexity: "simple|medium|complex"
  estimated_hours: 2-4
  
  context:
    why: "Business/technical reason this component exists"
    architectural_role: "How this fits in the universal platform"
    depends_on_tasks: ["list-of-task-ids"]
    enables_tasks: ["tasks-that-need-this"]
    references:
      masterplan: "@MASTERPLAN.md#relevant-section"
      adk_docs: 
        - "https://google.github.io/adk-docs/agents"
        - "https://google.github.io/adk-docs/runners"
      verification_notes: "What was verified in ADK docs for this task"
    
  adk_components:
    # IMPORTANT: These must be verified against ADK documentation
    # Do NOT guess class names or method signatures
    imports_needed:
      - "from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent"
      - "from google.adk.runners import InMemoryRunner"
      - "from google.adk.tools import FunctionTool"
    verified_patterns:  # Must reference specific doc sections
      - pattern: "Use InMemoryRunner for all execution"
        doc_ref: "https://google.github.io/adk-docs/runners#inmemoryrunner"
      - pattern: "Let ADK handle session management"
        doc_ref: "https://google.github.io/adk-docs/sessions"
    avoid_antipatterns:
      - "Don't implement custom session management"
      - "Don't create retry logic (ADK provides)"
      - "Don't hardcode business logic"
    
  implementation:
    creates:
      - path: "services/agent-engine/src/core/composition.py"
        purpose: "Universal agent factory"
        exports:
          - "class UniversalAgentFactory"
          - "def build_agent(spec: dict) -> BaseAgent"
      - path: "services/agent-engine/specs/agents/examples/analyzer.yaml"
        purpose: "Example LlmAgent specification"
        
    modifies:
      - path: "services/agent-engine/src/main.py"
        changes: ["Add agent composition endpoint"]
      - path: "docker-compose.yml"
        changes: ["Ensure agent-engine service configured"]
        
    uses_from_previous:
      - component: "SpecificationParser"
        from_task: "r1-t03"
        usage: "Parse agent specifications"
      - component: "ConfigLoader"
        from_task: "r1-t05"
        usage: "Load environment configuration"
    
  implementation_steps:
    - step: "Set up module structure"
      commands:
        - "mkdir -p services/agent-engine/src/core"
        - "touch services/agent-engine/src/core/composition.py"
    
    - step: "Implement agent factory"
      focus:
        - "Create UniversalAgentFactory class"
        - "Add build_agent method for each type"
        - "Implement tool loading logic"
        - "Add context injection for templates"
      
    - step: "Create example specifications"
      focus:
        - "Design YAML structure for agents"
        - "Include all required fields"
        - "Add example for each agent type"
    
    - step: "Write comprehensive tests"
      focus:
        - "Unit tests for factory methods"
        - "Integration tests with ADK"
        - "Specification validation tests"
    
  validation:
    commands:
      - desc: "Verify ADK agent creation"
        run: "python -c 'from core.composition import UniversalAgentFactory; factory = UniversalAgentFactory(); print(factory)'"
        expects: "Factory instance created"
        
      - desc: "Test LlmAgent creation from spec"
        run: "python tests/test_llm_agent_creation.py"
        expects: "All tests pass"
        
      - desc: "Validate example specifications"
        run: "python scripts/validate_specs.py specs/agents/examples/"
        expects: "All specs valid"
        
    endpoints:
      - method: "POST"
        path: "/agents/compose"
        body: "@specs/agents/examples/analyzer.yaml"
        expects: "200 with agent_id"
        
    integration:
      - desc: "Create and execute agent from spec"
        steps:
          - "Load specification"
          - "Create agent via factory"
          - "Execute with InMemoryRunner"
          - "Verify output"
    
  success_criteria:
    - "Agent factory creates all ADK agent types"
    - "Specifications validate and parse correctly"
    - "Tools load and attach to agents"
    - "Context injection works in templates"
    - "Tests achieve 80% coverage"
    
  session_notes:
    decisions_made:
      - "Specification schema version chosen"
      - "Factory pattern implementation"
      - "Error handling strategy"
    patterns_established:
      - "Agent building pattern for reuse"
      - "Specification structure"
      - "Tool loading approach"
    context_for_next:
      - "Factory interface for workflow agents"
      - "Specification format to maintain"
```

## Task Generation Rules

### 0. VERIFICATION REQUIREMENT
**Every technical detail MUST be verified** before including in a task:
- **ADK Components**: Verify exact class names, methods, and parameters at https://google.github.io/adk-docs/
- **Import Paths**: Confirm correct import statements from the documentation
- **Method Signatures**: Look up exact parameters and return types
- **Patterns**: Reference specific documentation examples
- **If Cannot Verify**: Mark as "NEEDS_VERIFICATION" with a note to check during implementation

### 1. Task Sizing Guidelines
- **Simple Tasks** (1-2 hours): Basic setup, configuration, simple features
- **Medium Tasks** (2-3 hours): Single component with tests
- **Complex Tasks** (3-4 hours): Multi-component integration, complex logic

### 2. Dependency Management
- Each task must explicitly list dependencies
- No circular dependencies allowed
- Tasks within a release can have dependencies
- Later releases depend on entire previous releases

### 3. ADK Compliance Rules
Every task must:
- Reference specific ADK documentation URLs
- List exact imports needed from google.adk (verified)
- Specify which ADK patterns to follow (with doc references)
- Explicitly state what NOT to build (ADK handles it)

### 4. Validation Requirements
Each task must include:
- At least 3 validation commands
- API endpoint tests if applicable
- Integration test scenario
- Success criteria checklist
- Note which validations were verified against docs

### 5. Context Preservation
Each task must specify:
- What patterns it establishes
- What decisions affect future tasks
- What interfaces must be maintained
- What should be added to project-context.md

## Specific Tasks to Generate

### Release 1: Foundation (5 tasks)
```yaml
r1-t01-project-setup:
  focus: "Monorepo structure with Python/ADK setup"
  creates: ["Project structure", "Virtual environment", "ADK installation"]
  
r1-t02-adk-verification:
  focus: "Verify all ADK components work"
  creates: ["ADK test script", "Import verification", "Basic agent test"]
  
r1-t03-specification-system:
  focus: "YAML/JSON specification parser and validator"
  creates: ["Specification models", "Parser", "Validator", "Examples"]
  
r1-t04-database-setup:
  focus: "Prisma schema for execution and audit storage"
  creates: ["Schema", "Models", "Migrations", "CRUD operations"]
  
r1-t05-configuration-loader:
  focus: "Hierarchical configuration system"
  creates: ["Config loader", "Environment overrides", "Validation"]
```

### Release 2: Composition (6 tasks)
```yaml
r2-t01-agent-factory-base:
  focus: "Base factory structure and interfaces"
  
r2-t02-llm-agent-builder:
  focus: "LlmAgent creation from specifications"
  
r2-t03-workflow-agents:
  focus: "Sequential, Parallel, Loop agent builders"
  
r2-t04-custom-agents:
  focus: "BaseAgent extension support"
  
r2-t05-runner-integration:
  focus: "InMemoryRunner integration"
  
r2-t06-composition-tests:
  focus: "Comprehensive test suite"
```

### Release 3: Tools (4 tasks)
```yaml
r3-t01-tool-registry:
  focus: "Core registry with registration API"
  
r3-t02-tool-loading:
  focus: "Dynamic tool loading and FunctionTool wrapping"
  
r3-t03-builtin-tools:
  focus: "Standard tool library"
  
r3-t04-tool-collections:
  focus: "Collections and categories"
```

### Release 4: Workflows (5 tasks)
```yaml
r4-t01-template-system:
  focus: "Workflow template parser and validator"
  
r4-t02-workflow-engine:
  focus: "Core execution engine with ADK"
  
r4-t03-conditional-workflows:
  focus: "Advanced patterns (conditional, loops)"
  
r4-t04-workflow-testing:
  focus: "Test suite for workflows"
  
r4-t05-workflow-examples:
  focus: "Example workflows for all patterns"
```

### Release 5: Sessions (4 tasks)
```yaml
r5-t01-session-orchestrator:
  focus: "Multi-backend session management"
  
r5-t02-memory-backend:
  focus: "InMemorySessionService integration"
  
r5-t03-redis-backend:
  focus: "Redis session persistence"
  
r5-t04-session-testing:
  focus: "Session management tests"
```

### Release 6: API (5 tasks)
```yaml
r6-t01-core-endpoints:
  focus: "Health, metrics, configuration"
  
r6-t02-agent-endpoints:
  focus: "Agent composition and management"
  
r6-t03-workflow-endpoints:
  focus: "Workflow execution and monitoring"
  
r6-t04-tool-endpoints:
  focus: "Tool registry management"
  
r6-t05-api-testing:
  focus: "Complete API test suite"
```

### Release 7: Integration (4 tasks)
```yaml
r7-t01-system-integration:
  focus: "Connect all components"
  
r7-t02-e2e-testing:
  focus: "End-to-end test scenarios"
  
r7-t03-performance-testing:
  focus: "Load and performance tests"
  
r7-t04-deployment-prep:
  focus: "Docker, documentation, scripts"
```

## Project Context File to Create

### project-context.md
```markdown
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
- **Agents**: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
- **Runtime**: InMemoryRunner (primary), run/run_async methods
- **Sessions**: InMemorySessionService, custom backends
- **Tools**: FunctionTool for explicit wrapping, automatic for most

## Specification Standards
- Version: agent-engine/v1
- Location: specs/{agents,workflows,tools,models}/
- Format: YAML with JSON Schema validation
- Required fields: apiVersion, kind, metadata, spec

## Established Patterns
[This section updated by each task]

## Interface Contracts
[This section updated by each task]

## Task Completion Tracking
[This section updated as tasks complete]
```

## Validation Script to Create

### validation/validate-tasks.py
```python
#!/usr/bin/env python3
"""Validate all task files for completeness and dependencies."""

import yaml
import sys
from pathlib import Path

def validate_task_file(filepath):
    """Validate a single task file."""
    with open(filepath) as f:
        task = yaml.safe_load(f)
    
    # Check required fields
    required = ['task', 'context', 'implementation', 'validation']
    for field in required:
        if field not in task:
            print(f"ERROR: {filepath} missing required field: {field}")
            return False
    
    # Check task has ID
    if 'id' not in task['task']:
        print(f"ERROR: {filepath} missing task.id")
        return False
    
    # Check dependencies exist
    # ... additional validation ...
    
    return True

def main():
    """Validate all tasks."""
    tasks_dir = Path('tasks')
    all_valid = True
    
    for task_file in tasks_dir.glob('r*/r*.yaml'):
        if not validate_task_file(task_file):
            all_valid = False
    
    if all_valid:
        print("✅ All tasks valid!")
    else:
        print("❌ Validation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Instructions for Claude Code

### CRITICAL: No Assumptions Policy
**You MUST NOT guess or assume any implementation details.** When creating tasks:
- If uncertain about an ADK component → Check https://google.github.io/adk-docs/
- If unclear about architecture → Reference @MASTERPLAN.md
- If ambiguous about dependencies → Verify in the documentation
- If unsure about patterns → Look up the specific ADK examples

**Use web_search to verify:**
- Exact ADK class names and imports
- Correct method signatures
- Proper initialization parameters
- Best practices for each component

### Task Generation Steps

1. **Read @MASTERPLAN.md** to understand the universal agent engine architecture
2. **Verify ADK components** at https://google.github.io/adk-docs/ for accuracy
3. **Create the directory structure** exactly as specified above
4. **Generate releases.yaml** with all 7 releases defined
5. **Create all task YAML files** following the template, ensuring:
   - Each task is self-contained and executable
   - Dependencies are explicit
   - ADK patterns are correctly specified (verified against docs)
   - Validation commands are accurate
   - No guessed implementations
6. **Generate project-context.md** with initial architecture decisions
7. **Create adk-patterns.md** with verified ADK best practices
8. **Generate validation script** to verify task completeness
9. **Create task-dependencies.md** showing the dependency graph

## Quality Checklist for Generated Tasks

Each task file must have:
- [ ] Unique ID following rX-tYY pattern
- [ ] Clear complexity rating and time estimate
- [ ] Explicit task dependencies listed
- [ ] ADK components and patterns specified
- [ ] Complete implementation steps
- [ ] At least 3 validation commands
- [ ] Success criteria defined
- [ ] Session notes for context preservation

## Remember

This is a UNIVERSAL platform, not domain-specific. Every task should:
- Support ANY type of agent or workflow
- Use specifications for ALL configuration
- Leverage ADK's built-in capabilities
- Avoid hardcoding business logic
- Enable plugin-based extensibility

Generate comprehensive task files that future Claude Code sessions can execute autonomously to build this universal agent orchestration platform!