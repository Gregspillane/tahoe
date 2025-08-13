# Project Tahoe - Agent Engine Architectural Blueprint v2.1

**Universal Agent Orchestration Platform**

This document has been validated against the official Google Agent Development Kit (ADK) documentation at https://google.github.io/adk-docs/

**Validation Status**: ✅ Verified against official ADK documentation (2025-08-13)  
**ADK Version Compatibility**: google-adk (Python package)  
**Documentation References**: 
- Main Docs: https://google.github.io/adk-docs/
- GitHub: https://github.com/google/adk-python
- API Reference: https://google.github.io/adk-docs/api-reference/python/

---

## Executive Summary

**Service Name**: `agent-engine`  
**Purpose**: Universal multi-agent orchestration platform for any domain  
**Architecture**: Generalizable microservice built on Google ADK with dynamic agent composition  
**Development Approach**: Configuration-driven agent definitions with runtime flexibility  

### Implementation Scope
- **Core Service**: Universal agent orchestration framework leveraging full ADK capabilities
- **Agent Ecosystem**: Dynamic agent composition from specifications with tool plugins
- **Design Goal**: Maximum flexibility while maintaining structured execution patterns

### Core Capabilities
1. **Dynamic Agent Composition**: Create any agent type from JSON/YAML specifications
2. **Universal Tool Registry**: Plugin-based tool system with runtime registration
3. **Workflow Engine**: Support for any workflow pattern (sequential, parallel, conditional, custom)
4. **Model Abstraction**: Transparent model switching with fallback strategies
5. **Session Management**: Full ADK session capabilities with multiple persistence options
6. **Real-time Orchestration**: Streaming execution with event-driven architecture

## Configuration Management

### Hierarchical Environment System

1. **Root .env File (Base Configuration)**
   - Contains ALL configuration variables for the entire monorepo
   - Service configs use prefixes (e.g., `AGENT_ENGINE_*`, `AUTH_SERVICE_*`)
   - Shared infrastructure settings (`DATABASE_*`, `REDIS_*`) without prefixes
   - Model API keys for ADK integration
   - Sensitive values marked with `CHANGE_THIS_` placeholders

2. **config/ Directory (Environment Overrides)**
   - `development.env` - Local development overrides (DEBUG logging, localhost)
   - `staging.env` - Staging environment settings (future)
   - `production.env` - Production configuration (future)

3. **Configuration Hierarchy**
   ```
   .env (base) → config/{environment}.env (overrides) → runtime specifications
   ```
   Environment-specific files override base .env values, runtime specs override both.

4. **Key Patterns**
   ```
   # Shared Infrastructure (no prefix)
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # Service-Specific (prefixed)
   AGENT_ENGINE_PORT=8001
   AGENT_ENGINE_LOG_LEVEL=INFO
   AGENT_ENGINE_DB_SCHEMA=agent_engine
   AGENT_ENGINE_REDIS_NAMESPACE=agent:
   
   # ADK Model Configuration
   GEMINI_API_KEY=your-gemini-key
   ADK_DEFAULT_MODEL=gemini-2.0-flash
   ADK_TEMPERATURE=0.2
   ADK_MAX_TOKENS=8192
   ADK_SESSION_SERVICE=memory  # memory, redis, vertex
   ```

5. **Service Isolation**
   - Each service gets its own database schema
   - Each service gets its own Redis namespace
   - ADK handles model API keys via environment variables
   - Production secrets will be managed via HashiCorp Vault (future)

### Future Production Architecture (AWS)
- **Platform**: AWS EKS (Kubernetes) 
- **Secrets Management**: HashiCorp Vault

---

## System Architecture

### Core Design Principles
1. **ADK-Native Development**: Follow ADK patterns with full framework utilization
2. **Configuration-Driven**: 
   - Agent specifications in JSON/YAML (version controlled)
   - Dynamic tool registration and loading
   - Runtime workflow composition
   - Model configuration abstraction
3. **Universal Orchestration**: Support any workflow pattern and agent hierarchy
4. **Session-Centric**: ADK Session, State, and Memory with flexible persistence
5. **Plugin Architecture**: Extensible tool registry and model providers
6. **Observable by Default**: ADK tracing + custom metrics + event streaming
7. **Domain Agnostic**: No hardcoded business logic or domain assumptions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      agent-engine                               │
│  ┌───────────────────────────────────────────────────────┐     │
│  │          API Gateway (FastAPI)                        │     │
│  │    Authentication | Rate Limiting | Validation       │     │
│  └───────────────────────────────────────────────────────┘     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │         Universal Agent Orchestration                 │     │
│  │    Dynamic Agent Composition | Workflow Engine        │     │
│  │    Session Management | Tool Registry                 │     │
│  └───────────────────────────────────────────────────────┘     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │         Configuration Engine                          │     │
│  │    Agent Specs | Workflow Templates | Model Config    │     │
│  └───────────────────────────────────────────────────────┘     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │         Plugin System                                 │     │
│  │    Tool Registry | Model Abstraction | Extensions     │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                        │
     ┌──────────────────┼──────────────────┬─────────────────┐
     ▼                  ▼                  ▼                 ▼
┌──────────┐    ┌──────────────┐    ┌──────────────┐ ┌─────────────┐
│  Redis   │    │   Postgres   │    │  Model APIs  │ │  External   │
│  Cache/  │    │   (Prisma)   │    │ (via ADK)    │ │  Systems    │
│  Session │    │              │    │              │ │  (via API)  │
└──────────┘    └──────────────┘    └──────────────┘ └─────────────┘
```

### ADK Integration Architecture (Complete)

```
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE ADK FRAMEWORK                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Core Components (Fully Utilized)               │   │
│  │  - Runner (InMemoryRunner, run, run_async)             │   │
│  │  - Session Services (InMemorySessionService, etc.)     │   │
│  │  - State Management (persistent context)               │   │
│  │  - Event System (conversation history)                 │   │
│  │  - Tool Wrapping (FunctionTool, automatic wrapping)    │   │
│  │  - Streaming Support (bidirectional audio/video)       │   │
│  │  - Error Recovery (built-in resilience)               │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            AGENT TYPES (All Supported)                 │   │
│  │  ┌────────────┐ ┌──────────────┐ ┌─────────────────┐  │   │
│  │  │ LlmAgent   │ │   Workflow   │ │     Custom      │  │   │
│  │  │ (Agent)    │ │ Sequential   │ │   (BaseAgent)   │  │   │
│  │  │            │ │ Parallel     │ │                 │  │   │
│  │  │            │ │ Loop         │ │                 │  │   │
│  │  └────────────┘ └──────────────┘ └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            TOOLS & INTEGRATION                          │   │
│  │  - Function Tools (FunctionTool, automatic wrapping)   │   │
│  │  - Agent Tools (agents as tools)                       │   │
│  │  - Built-in Tools (google_search, etc.)                │   │
│  │  - External Integrations (APIs, databases)             │   │
│  │  - Multi-modal Support (text, audio, video)            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AGENT-ENGINE ABSTRACTIONS                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Universal Composition Layer                     │   │
│  │  - Agent Factory (from specifications)                 │   │
│  │  - Workflow Engine (template-driven)                   │   │
│  │  - Tool Registry (plugin system)                       │   │
│  │  - Model Abstraction (provider-agnostic)               │   │
│  │  - Session Orchestration (multi-persistence)           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Configuration Storage (Specification-Based)

**Agent Specifications**
- Stored as JSON/YAML files in `specs/agents/` directory
- Version controlled with git
- Supports any agent type (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, Custom)
- Dynamic tool and sub-agent composition
- Structure:
  ```yaml
  apiVersion: "agent-engine/v1"
  kind: "AgentSpec"
  metadata:
    name: "universal-analyzer"
    version: "1.0.0"
    tags: ["analysis", "configurable"]
  spec:
    agent:
      type: "llm"  # llm, sequential, parallel, loop, custom
      model: 
        primary: "gemini-2.0-flash"
        fallbacks: ["gemini-2.5-pro", "gemini-2.5-flash"]
      instruction_template: |
        You are a {role} specializing in {domain}.
        Your task is to {task_description}.
      parameters:
        temperature: 0.2
        max_tokens: 8192
    tools:
      - name: "analyze_content"
        source: "registry"
      - name: "custom_scorer"
        source: "inline"
        definition: "def custom_scorer(data: dict) -> float: ..."
    sub_agents:
      - spec_ref: "specialist-a"
        condition: "input.requires_a"
      - spec_ref: "specialist-b"
        condition: "input.requires_b"
  ```

**Workflow Templates**
- Stored as JSON/YAML in `specs/workflows/` directory
- Support conditional, parallel, sequential, and custom patterns
- Dynamic agent composition based on input
- Structure:
  ```yaml
  apiVersion: "agent-engine/v1"
  kind: "WorkflowTemplate"
  metadata:
    name: "adaptive-processing"
  spec:
    type: "conditional"
    parameters:
      input_schema: {...}
      output_schema: {...}
    steps:
      - id: "intake"
        agent_spec: "content-classifier"
        outputs: ["content_type", "complexity"]
      - id: "processing"
        type: "conditional"
        conditions:
          - if: "content_type == 'analysis'"
            then: 
              type: "parallel"
              agents: ["analyzer-a", "analyzer-b"]
          - if: "content_type == 'generation'"
            then: "content-generator"
      - id: "synthesis"
        agent_spec: "result-synthesizer"
        depends_on: ["processing"]
  ```

**Tool Registry**
- JSON/YAML specifications in `specs/tools/` directory
- Runtime registration via API
- Automatic validation and schema checking
- Structure:
  ```yaml
  apiVersion: "agent-engine/v1"
  kind: "ToolSpec"
  metadata:
    name: "analyze_sentiment"
  spec:
    description: "Analyzes sentiment of text"
    function_definition: |
      def analyze_sentiment(text: str, model: str = "default") -> dict:
          # Implementation here
          return {"sentiment": "positive", "confidence": 0.85}
    dependencies: ["nltk", "transformers"]
    categories: ["analysis", "nlp"]
    input_schema:
      type: "object"
      properties:
        text: {"type": "string"}
        model: {"type": "string", "default": "default"}
    output_schema:
      type: "object"
      properties:
        sentiment: {"type": "string"}
        confidence: {"type": "number"}
  ```

**Model Configurations**
- Provider-agnostic model settings
- Fallback strategies and load balancing
- Structure:
  ```yaml
  apiVersion: "agent-engine/v1"
  kind: "ModelConfig"
  metadata:
    name: "production-config"
  spec:
    primary:
      provider: "google"
      model: "gemini-2.0-flash"
      parameters:
        temperature: 0.2
        max_tokens: 8192
    fallbacks:
      - provider: "google"
        model: "gemini-2.5-pro"
        trigger_conditions: ["rate_limit", "error"]
      - provider: "google"
        model: "gemini-2.5-flash"
        trigger_conditions: ["error"]
    load_balancing:
      strategy: "round_robin"
      health_check_interval: 30
  ```

### Database Entities (Execution & Audit Storage)

**Session**
- ADK session tracking and state persistence
- Links to workflow executions and results
- Supports multiple persistence backends (memory, Redis, Vertex)

**Execution**
- Records of workflow and agent executions
- Performance metrics and timing data
- Error tracking and debugging information

**Result**
- Outputs from agent and workflow executions
- Structured data with schema validation
- Links to source sessions and configurations

**AuditLog**
- Complete audit trail of all system actions
- Configuration versions used for each execution
- User actions, system events, and security logs

**ToolRegistry**
- Runtime tool registration and management
- Version tracking and dependency management
- Usage analytics and performance metrics

**ConfigurationVersion**
- Tracks versions of all specifications
- Enables rollback and change tracking
- Links executions to specific config versions

*Full schema available in `/prisma/schema.prisma`*

---

## Core Workflows with ADK

### Dynamic Agent Composition

1. **Specification-Driven Agent Creation**
   - Agent specs loaded from JSON/YAML files
   - Dynamic tool loading from registry
   - Model configuration from templates
   - Runtime parameter injection

2. **Universal Agent Factory**
   ```python
   from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
   from google.adk.tools import FunctionTool
   
   class AgentCompositionService:
       def build_agent_from_spec(self, spec_name: str, context: dict = None) -> BaseAgent:
           """Build any agent type from specification"""
           spec = self.load_agent_spec(spec_name)
           
           if spec.agent.type == "llm":
               return self._build_llm_agent(spec, context)
           elif spec.agent.type == "sequential":
               return self._build_sequential_agent(spec, context)
           elif spec.agent.type == "parallel":
               return self._build_parallel_agent(spec, context)
           elif spec.agent.type == "loop":
               return self._build_loop_agent(spec, context)
           else:
               return self._build_custom_agent(spec, context)
       
       def _build_llm_agent(self, spec: dict, context: dict = None) -> LlmAgent:
           """Build LLM agent with dynamic configuration."""
           agent_spec = spec["agent"]
           tools = self._load_tools(spec.get("tools", []))
           sub_agents = self._build_sub_agents(spec.get("sub_agents", []), context)
           
           # Dynamic instruction building with context injection
           instruction = self._build_instruction(agent_spec["instruction_template"], context)
           
           return LlmAgent(
               name=spec["metadata"]["name"],
               model=agent_spec["model"]["primary"],
               instruction=instruction,
               description=spec["metadata"].get("description", ""),
               tools=tools,
               sub_agents=sub_agents,
               **agent_spec.get("parameters", {})
           )
       
       def _build_sequential_agent(self, spec: dict, context: dict = None) -> SequentialAgent:
           """Build sequential workflow agent."""
           sub_agents = self._build_sub_agents(spec.get("sub_agents", []), context)
           return SequentialAgent(
               name=spec["metadata"]["name"],
               sub_agents=sub_agents,
               description=spec["metadata"].get("description", "")
           )
   ```

### Workflow Engine

1. **Template-Based Workflow Execution**
   - Workflow templates define execution patterns
   - Dynamic agent composition based on input
   - Conditional routing and parallel execution
   - State management between steps

2. **Workflow Orchestration**
   ```python
   from google.adk.runners import InMemoryRunner
   
   class WorkflowEngine:
       async def execute_workflow(self, template_name: str, input_data: dict, session_id: str) -> dict:
           """Execute workflow from template"""
           template = self.load_workflow_template(template_name)
           context = {"input": input_data}
           
           # Build workflow agent based on template
           workflow_agent = self._build_workflow_agent(template, context)
           
           # Execute via ADK Runner
           runner = InMemoryRunner(workflow_agent, app_name="workflow_engine")
           session = runner.session_service().create_session(
               app_name="workflow_engine",
               user_id="system",
               session_id=session_id
           )
           
           results = []
           for event in runner.run_async(session.user_id, session.id, input_data):
               results.append(event)
           
           return self._build_output(template.output_schema, results)
   ```

### Session Management

1. **Multi-Backend Session Support**
   - Memory sessions for quick operations
   - Redis sessions for distributed processing
   - Vertex sessions for enterprise features
   - Session forking and merging

2. **Session Lifecycle Management**
   ```python
   from google.adk.sessions import InMemorySessionService
   from google.adk.runners import InMemoryRunner
   
   class SessionOrchestrator:
       def create_session(self, config: dict) -> str:
           """Create session with specified configuration"""
           backend = config.get("persistence", "memory")
           
           if backend == "memory":
               session_service = InMemorySessionService()
           elif backend == "redis":
               # Custom Redis session service implementation
               session_service = self._create_redis_session_service()
           elif backend == "vertex":
               # Vertex AI session service for enterprise
               session_service = self._create_vertex_session_service()
           
           session = session_service.create_session(
               app_name=config["app_name"],
               user_id=config["user_id"],
               initial_state=config.get("initial_state", {}),
               session_id=config.get("session_id")
           )
           
           return session.id
   ```

### Tool Registry System

1. **Dynamic Tool Registration**
   - Runtime tool registration via API
   - Automatic function wrapping by ADK
   - Schema validation and testing
   - Dependency management

2. **Tool Loading and Validation**
   ```python
   from google.adk.tools import FunctionTool
   
   class ToolRegistry:
       def register_tool(self, tool_spec: dict) -> bool:
           """Register new tool from specification"""
           # Validate specification
           self._validate_tool_spec(tool_spec)
           
           # Create function from definition
           tool_function = self._create_function(tool_spec["function_definition"])
           
           # Validate function signature
           self._validate_function(tool_function, tool_spec["input_schema"])
           
           # Wrap with FunctionTool if needed
           if tool_spec.get("wrap_explicitly", False):
               tool_function = FunctionTool(tool_function)
           
           # Register in registry
           self.tools[tool_spec["name"]] = {
               "function": tool_function,
               "spec": tool_spec,
               "created_at": datetime.now()
           }
           
           return True
       
       def get_tools_for_agent(self, tool_names: list) -> list:
           """Get tool functions for agent creation."""
           tools = []
           for name in tool_names:
               if name in self.tools:
                   tools.append(self.tools[name]["function"])
               elif name == "google_search":
                   from google.adk.tools import google_search
                   tools.append(google_search)
           return tools
   ```

---

## API Architecture

### Core Agent Operations
- `POST /agents/compose` - Create agent from specification
- `PUT /agents/{id}/reconfigure` - Modify agent configuration
- `GET /agents/specs` - List available agent specifications
- `POST /agents/specs` - Create new agent specification
- `DELETE /agents/{id}` - Remove agent instance

### Workflow Management
- `POST /workflows/execute` - Execute workflow from template
- `GET /workflows/templates` - List workflow templates
- `POST /workflows/templates` - Create workflow template
- `GET /workflows/{id}/status` - Monitor execution status
- `POST /workflows/{id}/stream` - Stream execution events (SSE)

### Session Operations
- `POST /sessions/create` - Create session with configuration
- `PUT /sessions/{id}/state` - Update session state
- `GET /sessions/{id}/history` - Get conversation history
- `POST /sessions/{id}/fork` - Fork session for branching
- `DELETE /sessions/{id}` - Clean up session

### Tool Registry
- `POST /tools/register` - Register new tool
- `GET /tools/registry` - List available tools
- `PUT /tools/{name}/update` - Update tool definition
- `DELETE /tools/{name}` - Remove tool
- `POST /tools/collections` - Create tool collections

### Model Management
- `GET /models/available` - List configured models
- `POST /models/configure` - Configure model settings
- `PUT /models/fallback` - Update fallback strategies
- `GET /models/health` - Check model availability

### Configuration Management
- `GET /specs/agents` - List agent specifications
- `GET /specs/workflows` - List workflow templates
- `GET /specs/tools` - List tool specifications
- `POST /specs/validate` - Validate specification format
- `PUT /specs/{type}/{name}` - Update specification

### Monitoring & Observability
- `GET /health` - Service health with ADK status
- `GET /metrics` - Operational metrics
- `GET /events/stream` - Real-time event stream (SSE)
- `GET /sessions/{id}/trace` - Get execution trace
- `GET /analytics/usage` - Usage analytics

*Full API documentation in `/docs/api.md`*

---

## Non-Functional Requirements

### Security
- Service token authentication for all endpoints
- Model API keys managed via environment variables
- Input validation before ADK processing
- Comprehensive audit logging with session tracking
- Role-based access control for specifications
- Encrypted session state for sensitive data

### Performance (ADK-Optimized)
- ADK handles tool invocation efficiently
- Configurable timeouts via agent parameters
- Native streaming for real-time updates
- Built-in error recovery and retries
- Database connection pooling (10 base, 20 max)
- Redis for configuration and session caching
- Async/await throughout for concurrency

### Observability (ADK-Enhanced)
- Session tracking via ADK runners
- Structured logging with session and execution IDs
- Custom metrics via FastAPI middleware
- Health checks include model availability
- Error reporting from ADK operations
- Real-time event streaming
- Performance analytics and usage tracking

### Scalability
- Horizontal scaling with stateless design
- ADK session services handle state persistence
- Tool registry supports distributed deployments
- Model load balancing and fallback strategies
- Container orchestration ready
- Event-driven architecture for loose coupling

---

## Technology Stack

### Core Frameworks
- **FastAPI**: REST API, SSE support, async processing
- **Google ADK**: Universal agent orchestration framework
  - `LlmAgent` (aliased as `Agent`) for LLM-based agents
  - `SequentialAgent`, `ParallelAgent`, `LoopAgent` for workflow orchestration
  - `BaseAgent` for custom agent implementations
  - `InMemoryRunner` as the core runtime component (run, run_async)
  - Session services: `InMemorySessionService`, etc.
  - `FunctionTool` for explicit tool wrapping
  - Native multi-model support with automatic fallback
- **Prisma**: Database ORM for execution and audit storage
- **Redis**: Configuration caching and session persistence

### ADK Components (Complete Integration)
```python
# Core ADK imports
from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, google_search
from google.adk.events import Event

# Extended integrations
from google.adk.evaluations import AgentEvaluator
```

### Model Support (Gemini-First Approach)
- **Primary**: Gemini models via ADK native integration
  - `gemini-2.0-flash` (default - balanced performance)
  - `gemini-2.5-pro` (advanced reasoning)
  - `gemini-2.5-flash` (fast processing)
  - `gemini-2.5-flash-lite` (lightweight operations)
- **Future**: Additional model providers via LiteLLM integration
  - OpenAI models (planned)
  - Anthropic models (planned)
  - Open source models via Ollama (planned)

### Infrastructure
- PostgreSQL 15 (execution and audit data)
- Redis 7 (caching and session state)
- Docker containers with multi-stage builds
- Python 3.9+ (ADK requirement)

*Full dependencies in `requirements.txt`*

---

## Development Roadmap

### Release 1: Universal Foundation

**Project Setup & Core Infrastructure**
- Initialize monorepo structure with services directory
- Set up Python virtual environment and install ADK via `pip install google-adk`
- Create hierarchical configuration system (.env + overrides)
- Implement universal configuration loader for JSON/YAML specifications
- Set up FastAPI application with async support

**Database & Persistence**
- Create Prisma schema for executions, sessions, and audit trails
- Implement multi-backend session service wrapper
- Create basic CRUD operations for all entities
- Set up database migrations and seeding
- Add comprehensive audit logging

**ADK Integration Foundation**
- Configure ADK with Gemini model support via environment
- Create universal agent factory for all agent types (LlmAgent, SequentialAgent, ParallelAgent, LoopAgent)
- Implement specification parser and validator
- Test agent execution with InMemoryRunner (run, run_async)
- Set up error handling and recovery patterns

**API Foundation**
- Create health check endpoint with ADK status
- Implement authentication and rate limiting middleware
- Set up request/response validation with Pydantic
- Create basic agent composition endpoints
- Add session management endpoints

### Release 2: Dynamic Composition Engine

**Agent Specification System**
- Design and implement agent specification schema
- Create agent factory supporting all ADK agent types
- Build specification validator with comprehensive error handling
- Implement dynamic agent composition from specs
- Add agent lifecycle management

**Tool Registry Platform**
- Design tool specification schema
- Implement runtime tool registration system
- Create tool validation and testing framework
- Build tool dependency management
- Add tool versioning and rollback capabilities

**Session Orchestration**
- Implement multi-backend session management
- Create session forking and merging capabilities
- Build session state synchronization
- Add session lifecycle hooks and cleanup
- Implement session-scoped agent instances

**Workflow Foundation**
- Design workflow template schema
- Implement basic workflow engine using ADK workflow agents
- Create conditional execution logic
- Build parallel and sequential execution patterns
- Add workflow state management

### Release 3: Advanced Orchestration

**Workflow Engine Enhancement**
- Implement complex conditional workflows
- Create dynamic routing based on content analysis
- Build workflow state checkpointing and recovery
- Add workflow performance optimization
- Implement workflow event system

**Model Abstraction Layer**
- Create universal model configuration system
- Implement automatic fallback strategies
- Build model health monitoring
- Add load balancing across model providers
- Create model performance analytics

**Real-time Processing**
- Implement Server-Sent Events for workflow streaming
- Create real-time execution monitoring
- Build live workflow modification capabilities
- Add bidirectional streaming support
- Implement event-driven architecture

**Advanced Tool System**
- Create tool collections and categories
- Implement tool performance monitoring
- Build tool security and sandboxing
- Add external tool integration (APIs, databases)
- Create tool marketplace functionality

### Release 4: Enterprise Features

**Production Capabilities**
- Implement comprehensive monitoring and alerting
- Create performance analytics and optimization
- Build A/B testing framework for configurations
- Add resource quota management
- Implement advanced security patterns

**Multi-tenancy & Isolation**
- Create tenant isolation for specifications
- Implement resource quotas per tenant
- Build tenant-specific model configurations
- Add tenant analytics and billing hooks
- Create tenant management APIs

**Enterprise Integration**
- Build webhook system for external integrations
- Create event publishing to external systems
- Implement enterprise authentication (SAML, OIDC)
- Add compliance and governance features
- Create backup and disaster recovery

**Marketplace & Sharing**
- Implement specification marketplace
- Create import/export functionality
- Build template sharing and versioning
- Add community-contributed tools and workflows
- Create specification certification system

---

## Project Structure (Universal Architecture)

```
tahoe-monorepo/
├── services/
│   ├── agent-engine/                    # Universal orchestration service
│   │   ├── src/
│   │   │   ├── main.py                  # FastAPI application
│   │   │   ├── core/                    # Core orchestration engine
│   │   │   │   ├── composition.py       # Agent composition service
│   │   │   │   ├── workflow.py          # Workflow engine
│   │   │   │   ├── session.py          # Session orchestration
│   │   │   │   ├── tools.py            # Tool registry
│   │   │   │   └── models.py           # Model abstraction
│   │   │   ├── services/               # Business services
│   │   │   │   ├── execution.py        # Execution management
│   │   │   │   ├── configuration.py    # Configuration loading
│   │   │   │   ├── validation.py       # Specification validation
│   │   │   │   └── monitoring.py       # Observability
│   │   │   ├── api/                    # API endpoints
│   │   │   │   ├── agents.py           # Agent operations
│   │   │   │   ├── workflows.py        # Workflow management
│   │   │   │   ├── sessions.py         # Session operations
│   │   │   │   ├── tools.py            # Tool registry
│   │   │   │   └── models.py           # Model management
│   │   │   ├── models/                 # Pydantic models
│   │   │   │   ├── specifications.py   # Spec models
│   │   │   │   ├── execution.py        # Execution models
│   │   │   │   └── api.py              # API models
│   │   │   └── utils/                  # Utilities
│   │   │       ├── parser.py           # Specification parser
│   │   │       ├── validator.py        # Validation utilities
│   │   │       └── helpers.py          # Helper functions
│   │   ├── specs/                      # Specification files
│   │   │   ├── agents/                 # Agent specifications
│   │   │   │   ├── examples/           # Example agent specs
│   │   │   │   │   ├── analyzer.yaml
│   │   │   │   │   ├── coordinator.yaml
│   │   │   │   │   └── specialist.yaml
│   │   │   │   └── templates/          # Reusable templates
│   │   │   ├── workflows/              # Workflow templates
│   │   │   │   ├── examples/           # Example workflows
│   │   │   │   │   ├── parallel-analysis.yaml
│   │   │   │   │   ├── conditional-routing.yaml
│   │   │   │   │   └── sequential-processing.yaml
│   │   │   │   └── templates/          # Reusable templates
│   │   │   ├── tools/                  # Tool specifications
│   │   │   │   ├── analysis/           # Analysis tools
│   │   │   │   ├── generation/         # Generation tools
│   │   │   │   ├── integration/        # Integration tools
│   │   │   │   └── utility/            # Utility tools
│   │   │   └── models/                 # Model configurations
│   │   │       ├── production.yaml     # Production config
│   │   │       ├── development.yaml    # Development config
│   │   │       └── templates/          # Config templates
│   │   ├── tests/                      # Comprehensive tests
│   │   │   ├── unit/                   # Unit tests
│   │   │   ├── integration/            # Integration tests
│   │   │   ├── e2e/                    # End-to-end tests
│   │   │   └── fixtures/               # Test data
│   │   └── Dockerfile                  # Service container
│   │
│   └── infrastructure/                  # Shared infrastructure
│       ├── prisma/
│       │   ├── schema.prisma           # Database schema
│       │   └── migrations/             # Database migrations
│       └── docker-compose.yml          # Infrastructure services
│
├── config/                             # Environment configurations
│   ├── development.env                 # Local overrides
│   ├── staging.env                     # Staging settings
│   └── production.env                  # Production config
│
├── scripts/                           # Utility scripts
│   ├── setup.sh                       # Development setup
│   ├── deploy.sh                      # Deployment script
│   └── migrate.sh                     # Database migration
│
├── docs/                              # Documentation
│   ├── api.md                         # API documentation
│   ├── specifications.md              # Specification guide
│   ├── examples/                      # Usage examples
│   └── deployment.md                  # Deployment guide
│
└── .env                               # Base configuration
```

---

## Development Standards

### Code Quality
- Type hints for all functions and classes
- Comprehensive docstrings with examples
- 85%+ test coverage across all modules
- Use ADK's built-in error handling patterns
- Follow ADK best practices and patterns

### ADK Implementation Patterns (Best Practices)
```python
# UNIVERSAL: Agent composition from specifications
# File: core/composition.py
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import FunctionTool

class UniversalAgentFactory:
    """Factory for creating any agent type from specifications."""
    
    def build_agent(self, spec: dict, context: dict = None) -> BaseAgent:
        """Build any agent type from specification."""
        agent_type = spec["agent"]["type"]
        
        if agent_type == "llm":
            return self._build_llm_agent(spec, context)
        elif agent_type == "sequential":
            return self._build_sequential_agent(spec, context)
        elif agent_type == "parallel":
            return self._build_parallel_agent(spec, context)
        elif agent_type == "loop":
            return self._build_loop_agent(spec, context)
        else:
            return self._build_custom_agent(spec, context)
    
    def _build_llm_agent(self, spec: dict, context: dict = None) -> LlmAgent:
        """Build LLM agent with dynamic configuration."""
        agent_spec = spec["agent"]
        tools = self._load_tools(spec.get("tools", []))
        sub_agents = self._build_sub_agents(spec.get("sub_agents", []), context)
        
        # Dynamic instruction building with context injection
        instruction = self._build_instruction(agent_spec["instruction_template"], context)
        
        return LlmAgent(
            name=spec["metadata"]["name"],
            model=agent_spec["model"]["primary"],
            instruction=instruction,
            description=spec["metadata"].get("description", ""),
            tools=tools,
            sub_agents=sub_agents,
            **agent_spec.get("parameters", {})
        )
    
    def _build_sequential_agent(self, spec: dict, context: dict = None) -> SequentialAgent:
        """Build sequential workflow agent."""
        sub_agents = self._build_sub_agents(spec.get("sub_agents", []), context)
        return SequentialAgent(
            name=spec["metadata"]["name"],
            sub_agents=sub_agents,
            description=spec["metadata"].get("description", "")
        )

# UNIVERSAL: Dynamic tool loading
# File: core/tools.py
from google.adk.tools import FunctionTool

class ToolRegistry:
    """Universal tool registry with runtime registration."""
    
    def register_tool(self, tool_spec: dict) -> callable:
        """Register tool from specification."""
        # Create function from specification
        tool_function = self._create_function_from_spec(tool_spec)
        
        # Validate function signature
        self._validate_tool_function(tool_function, tool_spec)
        
        # Optionally wrap with FunctionTool for explicit control
        if tool_spec.get("explicit_wrapping", False):
            tool_function = FunctionTool(tool_function)
        
        # Store in registry
        self.tools[tool_spec["metadata"]["name"]] = {
            "function": tool_function,
            "spec": tool_spec,
            "created_at": datetime.now()
        }
        
        return tool_function
    
    def load_tools(self, tool_refs: list) -> list:
        """Load tools by reference or inline definition."""
        tools = []
        for tool_ref in tool_refs:
            if tool_ref["source"] == "registry":
                tools.append(self.get_tool(tool_ref["name"]))
            elif tool_ref["source"] == "inline":
                tool_function = self._create_function_from_definition(tool_ref["definition"])
                tools.append(tool_function)
            elif tool_ref["source"] == "import":
                tool_function = self._import_tool(tool_ref["module"], tool_ref["name"])
                tools.append(tool_function)
        return tools

# UNIVERSAL: Workflow engine
# File: core/workflow.py
from google.adk.runners import InMemoryRunner

class WorkflowEngine:
    """Universal workflow execution engine."""
    
    async def execute_workflow(self, template_name: str, input_data: dict, session_id: str) -> dict:
        """Execute workflow from template."""
        template = self.load_workflow_template(template_name)
        
        # Build workflow agent based on template type
        if template["spec"]["type"] == "sequential":
            workflow_agent = self._build_sequential_workflow(template)
        elif template["spec"]["type"] == "parallel":
            workflow_agent = self._build_parallel_workflow(template)
        elif template["spec"]["type"] == "conditional":
            workflow_agent = self._build_conditional_workflow(template, input_data)
        
        # Execute via ADK Runner
        runner = InMemoryRunner(workflow_agent, app_name="workflow_engine")
        session = runner.session_service().create_session(
            app_name="workflow_engine",
            user_id="system",
            session_id=session_id
        )
        
        # Run workflow
        results = []
        for event in runner.run_async(session.user_id, session.id, input_data):
            results.append(event)
        
        return self._build_output(template["spec"].get("output_schema"), results)

# UNIVERSAL: Session management
# File: core/session.py
from google.adk.sessions import InMemorySessionService

class SessionOrchestrator:
    """Universal session management with multiple backends."""
    
    def create_session(self, config: dict) -> str:
        """Create session with specified backend."""
        backend = config.get("persistence", "memory")
        
        if backend == "memory":
            session_service = InMemorySessionService()
        elif backend == "redis":
            session_service = self._create_redis_session_service()
        elif backend == "vertex":
            session_service = self._create_vertex_session_service()
        else:
            raise ValueError(f"Unsupported session backend: {backend}")
        
        session = session_service.create_session(
            app_name=config["app_name"],
            user_id=config["user_id"],
            initial_state=config.get("initial_state", {}),
            session_id=config.get("session_id")
        )
        
        return session.id
```

### Specification Standards
```yaml
# Agent Specification Template
apiVersion: "agent-engine/v1"
kind: "AgentSpec"
metadata:
  name: "example-agent"
  version: "1.0.0"
  description: "Description of agent purpose"
  tags: ["category1", "category2"]
  author: "team@company.com"
  created_at: "2025-01-01T00:00:00Z"

spec:
  agent:
    type: "llm"  # llm, sequential, parallel, loop, custom
    model:
      primary: "gemini-2.0-flash"
      fallbacks: ["gemini-2.5-pro", "gemini-2.5-flash"]
      parameters:
        temperature: 0.2
        max_tokens: 8192
        timeout: 300
    instruction_template: |
      You are a {role} with expertise in {domain}.
      Your primary task is to {task}.
      
      Guidelines:
      - {guideline1}
      - {guideline2}
      
      Context variables: {context_vars}
    
  tools:
    - name: "tool1"
      source: "registry"
    - name: "tool2"
      source: "inline"
      definition: |
        def tool2(param: str) -> dict:
            return {"result": param.upper()}
    - name: "tool3"
      source: "import"
      module: "external_tools"
      function: "process_data"
  
  sub_agents:
    - spec_ref: "specialist-agent"
      condition: "input.requires_specialist"
    - spec_ref: "validator-agent"
      condition: "true"
  
  validation:
    input_schema:
      type: "object"
      properties:
        text: {"type": "string"}
        options: {"type": "object"}
    output_schema:
      type: "object"
      properties:
        result: {"type": "string"}
        confidence: {"type": "number"}
```

### Testing Standards
- Unit tests for all service components
- Integration tests for ADK workflows
- End-to-end tests for complete scenarios
- Performance tests for scalability
- Specification validation tests

### Deployment
- Docker containerization with multi-stage builds
- Environment-based configuration management
- ADK handles model connections transparently
- Session state persistence options
- Health checks and monitoring
- **Future**: AWS EKS deployment with Helm charts

### Documentation
- API documentation (OpenAPI/Swagger)
- Specification guides with examples
- Configuration management guides
- Deployment and operations procedures
- Architecture decision records (ADRs)

---

## Quick Reference

### Key Configuration Files
- `/services/agent-engine/specs/` - All specifications (agents, workflows, tools, models)
- `/services/infrastructure/prisma/schema.prisma` - Database schema
- `/.env` - Base environment configuration
- `/config/{environment}.env` - Environment overrides

### Key Implementation Files
- `/services/agent-engine/src/core/` - Core orchestration components
- `/services/agent-engine/src/api/` - API endpoints
- `/services/agent-engine/src/services/` - Business services
- `/services/agent-engine/src/main.py` - FastAPI application entry point

### Development Commands
```bash
# Install ADK and dependencies
pip install google-adk
pip install -r requirements.txt

# Set up environment
export GEMINI_API_KEY="your-api-key"

# Run locally
uvicorn main:app --reload --port 8001

# Test agent specifications
python -m tests.test_specifications

# Run with Docker
docker-compose up agent-engine

# Run tests
pytest tests/ -v --cov=src

# Validate specifications
python scripts/validate_specs.py

# Deploy (future)
kubectl apply -f k8s/
```

### ADK Best Practices
1. **Use appropriate agent types** - LlmAgent for reasoning, SequentialAgent/ParallelAgent/LoopAgent for workflows
2. **Leverage automatic function wrapping** - Functions passed directly, FunctionTool for explicit control
3. **Utilize sub_agents for composition** - Build hierarchical agent systems
4. **Use InMemoryRunner for execution** - Standard pattern: run/run_async
5. **Implement proper session management** - Choose appropriate persistence backend
6. **Enable streaming for real-time** - Native support for live interactions
7. **Follow error handling patterns** - Use ADK's built-in recovery mechanisms

### Specification Quick Tips
1. **Version all specifications** - Enable rollback and change tracking
2. **Use template variables** - Make specifications reusable across contexts
3. **Define clear schemas** - Validate inputs and outputs for reliability
4. **Implement conditions properly** - Use Python expressions for dynamic behavior
5. **Tag and categorize** - Enable discovery and organization
6. **Document thoroughly** - Include descriptions and usage examples

---