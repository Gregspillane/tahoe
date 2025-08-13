# Project Tahoe - Agent Engine Architectural Blueprint 

**Universal Agent Orchestration Platform**

This document has been validated and corrected against the official Google Agent Development Kit (ADK) documentation.

**Validation Status**: ✅ Verified against ADK documentation (2025-08-13)  
**ADK Compatibility**: google-adk Python package  
**Documentation Source**: https://google.github.io/adk-docs/  
**Repository**: https://github.com/google/adk-python  

> **Note**: This corrected version maintains the full Project Tahoe vision while fixing ADK-specific technical inaccuracies.

---

## Executive Summary

**Service Name**: `agent-engine`  
**Purpose**: Universal multi-agent orchestration platform for any domain  
**Architecture**: Generalizable microservice built on Google ADK with dynamic agent composition  
**Development Approach**: Configuration-driven agent definitions with runtime flexibility  

### Implementation Scope
- **Core Service**: Universal agent orchestration framework leveraging ADK capabilities
- **Agent Ecosystem**: Dynamic agent composition from specifications with tool plugins
- **Design Goal**: Maximum flexibility while maintaining structured execution patterns

### Core Capabilities
1. **Dynamic Agent Composition**: Create any agent type from JSON/YAML specifications using ADK's Agent/LlmAgent classes
2. **Universal Tool Registry**: Plugin-based tool system with runtime registration (functions passed directly to ADK)
3. **Workflow Engine**: Support for any workflow pattern (using sub_agents and coordination patterns)
4. **Model Abstraction**: Transparent model switching with fallback strategies
5. **Session Management**: ADK's built-in session capabilities with flexible persistence
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
   ```bash
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
   # Additional model keys as needed
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
1. **ADK-Native Development**: Follow ADK patterns while building universal orchestration
2. **Configuration-Driven**: 
   - Agent specifications in JSON/YAML (version controlled)
   - Dynamic tool registration and loading
   - Runtime workflow composition
   - Model configuration abstraction
3. **Universal Orchestration**: Support any workflow pattern and agent hierarchy
4. **Session-Centric**: ADK Session with flexible persistence options
5. **Plugin Architecture**: Extensible tool registry and model providers
6. **Observable by Default**: Comprehensive logging, metrics, and event streaming
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

### ADK Integration Architecture 

```python
# CORRECT ADK Imports and Usage
from google.adk.agents import Agent, LlmAgent, BaseAgent
from google.adk.tools import google_search  # Pre-built tools available

# Note: The following components from original masterplan are INCORRECT:
# - No SequentialAgent, ParallelAgent, LoopAgent classes exist
# - No FunctionTool class (functions are passed directly)
# - No complex Runner with run/run_async/run_live methods
# - Session services work differently than originally described
```

#### Actual ADK Architecture
1. **Agent Types**
   - `Agent` and `LlmAgent`: Core agent classes for LLM-based agents
   - `BaseAgent`: For custom agent implementations
   - Workflow patterns achieved through sub_agents and coordination

2. **Tool Integration**
   - Direct function passing (ADK handles wrapping automatically)
   - Pre-built tools like `google_search`
   - No need for complex tool registry at ADK level

3. **Execution Model**
   - Simpler execution patterns than originally described
   - ADK handles complexity internally
   - Focus on agent composition rather than execution orchestration

---

## Data Model

### Configuration Storage (Specification-Based)

**Agent Specifications**
- Stored as JSON/YAML files in `specs/agents/` directory
- Version controlled with git
- Supports agent creation using ADK's Agent/LlmAgent classes
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
      type: "llm"  # Maps to ADK's LlmAgent
      model: "gemini-2.0-flash"
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
  ```

**Workflow Templates**
- Stored as JSON/YAML in `specs/workflows/` directory
- Implemented using ADK's sub_agents and coordination patterns
- Dynamic agent composition based on input
- Structure maintained for configuration-driven approach

**Tool Registry**
- JSON/YAML specifications in `specs/tools/` directory
- Runtime registration via API
- Functions passed directly to ADK agents
- ADK handles automatic wrapping

**Model Configurations**
- Provider-agnostic model settings
- Primary support for Gemini models (ADK-optimized)
- Fallback strategies at application level

### Database Entities (Execution & Audit Storage)

**Session**
- Tracks ADK agent execution sessions
- Links to workflow executions and results
- Stores context for session continuity

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

## Core Workflows with ADK (Corrected Implementation)

### Dynamic Agent Composition

1. **Specification-Driven Agent Creation**
   ```python
   from google.adk.agents import Agent, LlmAgent
   
   class AgentCompositionService:
       def build_agent_from_spec(self, spec_name: str, context: dict = None):
           """Build agent from specification using ADK."""
           spec = self.load_agent_spec(spec_name)
           
           # Map spec type to ADK agent class
           if spec['agent']['type'] == 'llm':
               # Build instruction from template
               instruction = self._build_instruction(
                   spec['agent']['instruction_template'], 
                   context
               )
               
               # Load tools as Python functions
               tools = self._load_tools(spec.get('tools', []))
               
               # Create sub-agents if specified
               sub_agents = []
               for sub_spec in spec.get('sub_agents', []):
                   if self._evaluate_condition(sub_spec.get('condition'), context):
                       sub_agent = self.build_agent_from_spec(sub_spec['spec_ref'], context)
                       sub_agents.append(sub_agent)
               
               # Create ADK agent
               return LlmAgent(
                   name=spec['metadata']['name'],
                   model=spec['agent']['model'],
                   instruction=instruction,
                   tools=tools,
                   sub_agents=sub_agents if sub_agents else None,
                   description=spec['metadata'].get('description', '')
               )
   ```

2. **Universal Agent Factory**
   - Uses ADK's Agent/LlmAgent classes directly
   - No complex factory for non-existent agent types
   - Focus on configuration-driven instantiation

### Workflow Engine

1. **Template-Based Workflow Execution**
   - Workflow templates define execution patterns
   - Implemented using agent coordination and sub_agents
   - No separate workflow agent classes in ADK

2. **Workflow Orchestration**
   ```python
   class WorkflowEngine:
       async def execute_workflow(self, template_name: str, input_data: dict):
           """Execute workflow using ADK agents."""
           template = self.load_workflow_template(template_name)
           
           # Create coordinator agent with sub-agents
           coordinator = self._build_coordinator_agent(template)
           
           # Execute through ADK
           result = coordinator.run(input_data)
           
           return self._format_output(result, template.get('output_schema'))
   ```

### Session Management

1. **ADK Session Handling**
   ```python
   class SessionOrchestrator:
       def create_session(self, config: dict):
           """Create session for agent execution."""
           # ADK handles session internally during agent execution
           # We track additional metadata in our database
           session_id = self._generate_session_id()
           
           # Store session metadata
           self.db.create_session({
               'id': session_id,
               'config': config,
               'created_at': datetime.now()
           })
           
           return session_id
   ```

### Tool Registry System

1. **Dynamic Tool Registration**
   ```python
   class ToolRegistry:
       def register_tool(self, tool_spec: dict):
           """Register tool function for ADK agents."""
           # Create Python function from specification
           tool_function = self._create_function(tool_spec['definition'])
           
           # Store in registry (functions passed directly to ADK)
           self.tools[tool_spec['name']] = tool_function
           
           return True
       
       def get_tools_for_agent(self, tool_names: list):
           """Get tool functions for agent creation."""
           tools = []
           for name in tool_names:
               if name in self.tools:
                   tools.append(self.tools[name])
               elif name == 'google_search':
                   tools.append(google_search)  # ADK built-in
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
- `GET /health` - Service health status
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

### Performance
- ADK handles core agent execution efficiently
- Configurable timeouts via agent parameters
- Database connection pooling (10 base, 20 max)
- Redis for configuration and session caching
- Async/await throughout for concurrency
- Horizontal scaling with stateless design

### Observability
- Structured logging with session and execution IDs
- Custom metrics via FastAPI middleware
- Health checks include model availability
- Error reporting from ADK operations
- Real-time event streaming
- Performance analytics and usage tracking

### Scalability
- Horizontal scaling with stateless design
- Tool registry supports distributed deployments
- Model load balancing and fallback strategies
- Container orchestration ready
- Event-driven architecture for loose coupling

---

## Technology Stack 

### Core Frameworks
- **FastAPI**: REST API, SSE support, async processing
- **Google ADK**: Agent orchestration framework
  - `Agent` and `LlmAgent` for LLM-based agents
  - `BaseAgent` for custom agent implementations
  - Direct function passing as tools
  - Built-in session and state management
- **Prisma**: Database ORM for execution and audit storage
- **Redis**: Configuration caching and session persistence

### ADK Components (Actual Implementation)
```python
# CORRECT ADK imports
from google.adk.agents import Agent, LlmAgent, BaseAgent
from google.adk.tools import google_search  # Pre-built tools

# Note: Many components from original masterplan don't exist in ADK
```

### Model Support
- **Primary**: Gemini models via ADK native integration
  - `gemini-2.0-flash` (default - balanced performance)
  - Additional Gemini models as available
- **Future**: Additional model providers as ADK support expands

### Infrastructure
- PostgreSQL 15 (execution and audit data)
- Redis 7 (caching and session state)
- Docker containers with multi-stage builds
- Python 3.9+ (ADK requirement)

*Full dependencies in `requirements.txt`*

---

## Development Roadmap

### Release 1: Universal Foundation (Weeks 1-2)

**Project Setup & Core Infrastructure**
- Initialize monorepo structure with services directory
- Set up Python virtual environment and install ADK
- Create hierarchical configuration system (.env + overrides)
- Implement universal configuration loader for JSON/YAML specifications
- Set up FastAPI application with async support

**Database & Persistence**
- Create Prisma schema for executions, sessions, and audit trails
- Implement session tracking alongside ADK execution
- Create basic CRUD operations for all entities
- Set up database migrations and seeding
- Add comprehensive audit logging

**ADK Integration Foundation**
- Configure ADK with Gemini model support
- Create agent composition service using Agent/LlmAgent
- Implement specification parser and validator
- Test agent execution with direct function tools
- Set up error handling and recovery patterns

**API Foundation**
- Create health check endpoint
- Implement authentication and rate limiting middleware
- Set up request/response validation with Pydantic
- Create basic agent composition endpoints
- Add session management endpoints

### Release 2: Dynamic Composition Engine (Weeks 3-4)

**Agent Specification System**
- Design and implement agent specification schema
- Create agent factory using ADK's Agent/LlmAgent classes
- Build specification validator with comprehensive error handling
- Implement dynamic agent composition from specs
- Add agent lifecycle management

**Tool Registry Platform**
- Design tool specification schema
- Implement runtime tool registration system
- Create tool validation framework
- Build tool dependency management
- Add tool versioning capabilities

**Session Orchestration**
- Implement session tracking alongside ADK execution
- Create session state management
- Build session lifecycle hooks and cleanup
- Add session-scoped agent instances

**Workflow Foundation**
- Design workflow template schema
- Implement workflow engine using agent coordination
- Create conditional execution logic
- Build parallel execution using sub_agents
- Add workflow state management

### Release 3: Advanced Orchestration (Weeks 5-6)

**Workflow Engine Enhancement**
- Implement complex conditional workflows
- Create dynamic routing based on content analysis
- Build workflow state checkpointing and recovery
- Add workflow performance optimization
- Implement workflow event system

**Model Abstraction Layer**
- Create model configuration system
- Implement fallback strategies at application level
- Build model health monitoring
- Add load balancing logic
- Create model performance analytics

**Real-time Processing**
- Implement Server-Sent Events for workflow streaming
- Create real-time execution monitoring
- Build live workflow modification capabilities
- Add event-driven architecture
- Implement streaming support

**Advanced Tool System**
- Create tool collections and categories
- Implement tool performance monitoring
- Build tool validation and testing
- Add external tool integration (APIs, databases)
- Create tool discovery functionality

### Release 4: Enterprise Features (Weeks 7-8)

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
- Add community-contributed tools
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
│   │   │   │   ├── composition.py       # Agent composition using ADK
│   │   │   │   ├── workflow.py          # Workflow engine
│   │   │   │   ├── session.py          # Session management
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
│   │   │   ├── workflows/              # Workflow templates
│   │   │   ├── tools/                  # Tool specifications
│   │   │   └── models/                 # Model configurations
│   │   ├── tests/                      # Comprehensive tests
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
- Follow Python PEP 8 standards
- Use ADK's patterns and best practices

### ADK Implementation Patterns 
```python
# CORRECT: Agent composition from specifications
from google.adk.agents import Agent, LlmAgent

class UniversalAgentFactory:
    """Factory for creating agents from specifications using ADK."""
    
    def build_agent(self, spec: dict, context: dict = None):
        """Build agent using ADK's actual classes."""
        agent_type = spec["agent"]["type"]
        
        if agent_type == "llm":
            # Build instruction from template
            instruction = self._build_instruction(
                spec["agent"]["instruction_template"], 
                context
            )
            
            # Load tools as Python functions
            tools = self._load_tool_functions(spec.get("tools", []))
            
            # Create sub-agents if needed
            sub_agents = self._build_sub_agents(spec.get("sub_agents", []), context)
            
            # Use ADK's LlmAgent
            return LlmAgent(
                name=spec["metadata"]["name"],
                model=spec["agent"]["model"],
                instruction=instruction,
                tools=tools,
                sub_agents=sub_agents if sub_agents else None,
                description=spec["metadata"].get("description", "")
            )
        else:
            # Custom agent types built on BaseAgent
            return self._build_custom_agent(spec, context)

# CORRECT: Tool loading - functions passed directly
class ToolRegistry:
    """Registry for tool functions."""
    
    def load_tools(self, tool_refs: list) -> list:
        """Load tool functions for ADK agents."""
        tools = []
        for tool_ref in tool_refs:
            if tool_ref["source"] == "registry":
                # Get registered function
                func = self.get_tool_function(tool_ref["name"])
                tools.append(func)
            elif tool_ref["source"] == "inline":
                # Create function from definition
                func = self._create_function(tool_ref["definition"])
                tools.append(func)
            elif tool_ref["name"] == "google_search":
                # Use ADK's built-in tool
                from google.adk.tools import google_search
                tools.append(google_search)
        return tools

# CORRECT: Workflow using agent coordination
class WorkflowEngine:
    """Workflow engine using ADK agents."""
    
    async def execute_workflow(self, template_name: str, input_data: dict):
        """Execute workflow using agent coordination."""
        template = self.load_workflow_template(template_name)
        
        # Build coordinator agent with sub-agents for workflow
        steps = template["spec"]["steps"]
        sub_agents = []
        
        for step in steps:
            agent = self.agent_factory.build_agent(step["agent_spec"])
            sub_agents.append(agent)
        
        # Create coordinator to orchestrate workflow
        coordinator = LlmAgent(
            name=f"{template_name}_coordinator",
            model="gemini-2.0-flash",
            instruction=self._build_workflow_instruction(template),
            sub_agents=sub_agents
        )
        
        # Execute through coordinator
        result = coordinator.run(input_data)
        return result
```

### Testing Standards
- Unit tests for all service components
- Integration tests for ADK agent creation and execution
- End-to-end tests for complete scenarios
- Performance tests for scalability
- Specification validation tests

### Deployment
- Docker containerization with multi-stage builds
- Environment-based configuration management
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
1. **Use Agent/LlmAgent classes** - These are the actual ADK agent classes
2. **Pass functions directly as tools** - ADK handles wrapping automatically
3. **Utilize sub_agents for workflows** - Instead of non-existent workflow classes
4. **Keep execution simple** - ADK handles complexity internally
5. **Focus on composition** - Build complex behavior through agent composition

### Specification Quick Tips
1. **Version all specifications** - Enable rollback and change tracking
2. **Use template variables** - Make specifications reusable across contexts
3. **Define clear schemas** - Validate inputs and outputs for reliability
4. **Implement conditions properly** - Use Python expressions for dynamic behavior
5. **Tag and categorize** - Enable discovery and organization
6. **Document thoroughly** - Include descriptions and usage examples

---