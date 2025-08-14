# Project Tahoe - Architecture Decisions

## Core Architecture Patterns

### 0. Self-Contained Service Architecture (Microservice Independence)
**Pattern**: Each service owns its complete infrastructure stack including data persistence
**Decision Rationale**: 
- Eliminates cross-service startup dependencies
- Follows microservice best practice of service autonomy
- Prevents dependency inversion anti-patterns
- Simplifies development and deployment workflows

**Implementation**:
- Agent-engine includes PostgreSQL + Redis in its docker-compose.yml
- No separate infrastructure service dependencies
- Single command startup per service: `cd services/agent-engine && make docker-up`
- Future auth/billing services will follow same self-contained pattern

**Benefits**:
- Eliminates startup crashes from cross-service dependencies
- Simplifies development workflow to single command
- Each service can be developed, tested, and deployed independently
- No shared infrastructure complexity until actually needed (YAGNI principle)

**Lessons Learned**:
- Dependency inversion (core service depending on infrastructure service) creates fragile systems
- Premature optimization for shared infrastructure adds complexity without benefit
- Microservice "independence" means owning your data, not just your code

### 1. Specification-Driven Design
**Pattern**: All agents, workflows, and tools defined via YAML/JSON specifications
**Implementation**: 
- Specifications stored in `specs/` directory hierarchy
- Runtime parsing and validation
- Version control for all specifications
**Benefits**: 
- No code changes needed for new agents
- Easy versioning and rollback
- Clear separation of configuration and logic

### 2. Universal Agent Factory with Builder Pattern ✅ **ENHANCED**
**Pattern**: Factory with registered builders for different agent types
**Implementation**:
```python
class UniversalAgentFactory:
    def __init__(self):
        self.builders: Dict[str, AgentBuilder] = {}
        self._register_builders()
    
    def build_agent(spec: dict, context: dict) -> BaseAgent:
        # Use builder if available, fallback to direct dispatch
        if agent_type in self.builders:
            return self.builders[agent_type].build(spec, context)
```
**Supports**: LlmAgent (via LlmAgentBuilder), SequentialAgent, ParallelAgent, LoopAgent, Custom (BaseAgent)
**Features**:
- **Builder Registration**: Automatic discovery and registration of agent builders
- **Flexible Architecture**: Builder pattern for complex agents, direct dispatch for simple ones
- **Backward Compatibility**: Existing direct methods maintained for workflow agents
- **Sub-Agent Factory**: Circular reference support for recursive agent building

### 3. LLM Agent Builder Pattern ✅ **NEW**
**Pattern**: Specialized builder for LLM agents with advanced feature support
**Implementation**:
```python
class LlmAgentBuilder(AgentBuilder):
    def __init__(self, tool_registry=None):
        self.tool_loader = ToolLoader(tool_registry)
        self.sub_agent_factory = None  # Set by factory for recursion
    
    def build(self, spec: AgentSpec, context: AgentContext) -> LlmAgent:
        # Advanced instruction processing with context variables
        # Multi-source tool loading (registry, inline, import, builtin)
        # Fallback model configuration
        # Safe condition evaluation for sub-agents
```
**Key Features**:
- **Multi-Source Tool Loading**: Registry, inline definitions, module imports, built-in ADK tools
- **Context Variable Substitution**: Template processing with ${variable} syntax and fallback placeholders
- **Fallback Model Support**: Primary/fallback model configuration with automatic parameter passing
- **Secure Tool Execution**: Namespace isolation for inline tool definitions
- **Safe Condition Evaluation**: No eval() usage, secure parsing for sub-agent conditions
- **Comprehensive Validation**: Specification validation before agent creation

### 4. Multi-Source Tool Loading Architecture ✅ **NEW**
**Pattern**: Flexible tool loading from multiple sources with validation
**Implementation**:
```python
class ToolLoader:
    def load_tools(self, tool_specs: List[Dict]) -> List[Callable]:
        # Support multiple sources: registry, inline, import, builtin
        
    def _load_single_tool(self, spec: Dict) -> Optional[Callable]:
        source = spec.get('source', 'registry')
        if source == 'registry': return self._load_from_registry(spec['name'])
        elif source == 'builtin': return self._load_built_in(spec['name'])  
        elif source == 'inline': return self._create_inline_tool(spec)
        elif source == 'import': return self._import_tool(spec)
```
**Tool Sources**:
- **Registry**: Pre-registered tools from tool registry
- **Built-in**: Native ADK tools like google_search with proper error handling
- **Inline**: Function definitions executed in isolated namespaces (secure)
- **Import**: Dynamic module imports for external libraries
**Benefits**:
- **Maximum Flexibility**: Specifications can use any tool source
- **Security**: Inline tools executed in isolated namespaces
- **Validation**: Function signature validation and error reporting
- **Performance**: Registry caching and built-in tool optimization

### 5. Centralized Configuration System
**Pattern**: Environment-aware configuration with deployment flexibility
**Implementation**:
- **Development**: Root `.env` file with Pydantic Settings
- **Staging/Production**: Environment variables from Helm/Vault
- **Structured Config Classes**: Database, Redis, ADK, Security, Observability
- **Runtime Validation**: Environment-specific validation rules
**Loading Order**: Environment variables → .env file → defaults
**Key Features**:
- Graceful degradation in development
- Strict validation in production
- Centralized service configuration
- Docker-compatible mounting

### 4. Plugin-Based Tool System
**Pattern**: Runtime tool registration with dynamic loading
**Implementation**:
- Tool registry with validation
- Automatic function wrapping (ADK feature)
- Explicit FunctionTool when needed
**Categories**: Analysis, Generation, Integration, Utility
**Loading Sources**:
- Registry: Pre-registered tools
- Inline: Function definitions in specs
- Import: Module-based tools

### 5. Hierarchical Configuration Management ✅ **NEW**
**Pattern**: Multi-level configuration with environment-specific overrides
**Implementation**:
- Base `.env` file (project root)
- Environment-specific overrides (`config/development.env`, etc.)
- Runtime specification overrides (`specs/config/`)
- Pydantic-settings with validation
**Benefits**:
- Environment-aware deployment patterns
- Runtime configuration changes without code deployment
- Service isolation via database schemas and Redis namespaces
- Sensitive value masking for security

### 6. ADK Dev UI Integration Pattern ✅ **UPDATED**
**Pattern**: Visual development interface for agent testing and debugging with specification path resolution
**Implementation**:
- DevUILauncher service with automatic agent discovery
- AgentDiscovery utility with correct YAML specification path resolution
- Relative path calculation from agents directory (not specs directory)
- Environment-aware configuration (port 8002, avoiding conflicts)
- One-command setup via Makefile targets
- Full integration with UniversalAgentFactory
**Benefits**:
- Real-time visual agent testing and debugging
- End-to-end agent creation from specifications
- Interactive development workflow with immediate feedback
- Browser-based interface with Events tab for trace inspection
- Production-ready visual validation for R2 Composition development
**Key Pattern**: Specification paths must be relative to agents directory for factory compatibility

### 7. Service Isolation Architecture ✅ **NEW**
**Pattern**: Multi-service sharing with logical isolation
**Implementation**:
- **Database**: PostgreSQL schemas (`agent_engine`, `auth_service`, etc.)
- **Redis**: Namespaced keys (`agent:key`, `auth:key`, etc.)
- **Configuration**: Service-prefixed environment variables
- **Service Discovery**: Environment-aware URL generation
**Benefits**:
- Resource efficiency (shared infrastructure)
- Clear service boundaries
- Environment-specific deployment patterns

### 8. Real ADK v1.10.0 Integration Patterns ✅ **NEW**
**Pattern**: Production-validated patterns for real ADK integration
**Implementation**:
- **Model Parameters**: Use `google.genai.types.GenerateContentConfig` for LLM model configuration
- **Fail-Fast Architecture**: Single primary model only, no fallback_models
- **Workflow Agent Simplicity**: Basic constructor patterns (name, sub_agents, description)
- **Parameter Validation**: Real ADK rejects extra parameters, strict validation required
**Key Patterns**:
```python
# Correct LLM model parameter handling
from google.genai import types
config = types.GenerateContentConfig(
    temperature=0.2,
    max_output_tokens=8192
)
agent = LlmAgent(
    name="agent_name",
    model="gemini-2.5-flash-lite",
    instruction="instruction",
    generate_content_config=config
)

# Correct workflow agent creation
workflow = SequentialAgent(
    name="workflow_name",
    sub_agents=[agent1, agent2],
    description="description"
)
```
**Benefits**:
- Production compatibility with real ADK
- Fail-fast error detection
- Simplified parameter management
- Future-proof for ADK updates

## ADK Integration Points

### Validated ADK Patterns ✅
**Critical Requirements** (Production compliance):
- **Agent Naming**: Must use valid Python identifiers (underscores, not hyphens)
- **Session Access**: `runner.session_service` (property, not method call)
- **LoopAgent Structure**: Uses `sub_agents` as list parameter, not `sub_agent`
- **Model Parameters**: Set at runtime via RunConfig, not during agent creation
- **Agent Reuse**: Each workflow must use separate agent instances

### Agent Creation
- **LlmAgent**: Primary agent type for LLM interactions (aliased as Agent)
- **Workflow Agents**: Sequential, Parallel, Loop for orchestration
- **BaseAgent**: Extension point for custom agents
- **Validation**: All agent names validated against Python identifier rules

### Execution Runtime
- **InMemoryRunner**: Primary execution component, session service built-in
- **Methods**: `run()` for sync, `run_async()` for streaming
- **Session Access**: Property pattern: `runner.session_service`
- **Session Creation**: Support both sync (`create_session_sync`) and async patterns

### Session Management
- **InMemorySessionService**: Default session backend
- **Session Creation**: Handle both sync/async patterns gracefully
- **State Management**: ADK handles persistence and recovery
- **Custom Backends**: Redis, Vertex AI (planned)

### Tool Integration
- **Automatic Wrapping**: Most Python functions work directly (preferred)
- **FunctionTool**: Explicit wrapping for complex tools
- **Built-in Tools**: google_search and others from ADK
- **Mixed Patterns**: Support automatic + explicit + built-in tools in same agent

## Data Flow Architecture

```
User Request → API Gateway → Specification Loader → Agent Factory
                                                           ↓
                                                    Agent Instance
                                                           ↓
                                                    InMemoryRunner
                                                           ↓
                                                    Session Service
                                                           ↓
                                                    Tool Execution
                                                           ↓
                                                    Result Storage → Response
```

## Service Boundaries

### agent-engine Service
**Responsibilities**:
- Agent composition and management
- Workflow execution
- Tool registry
- Session orchestration
- API endpoints

**Not Responsible For**:
- Authentication (future auth-service)
- Direct model API calls (handled by ADK)
- Business logic (stays in specifications)

## Database Schema Design ✅ **IMPLEMENTED**

### Core Entities (Prisma Schema)
1. **Session**: ADK session tracking with state and metadata storage
2. **Execution**: Agent/workflow execution records with timing and status
3. **Result**: Intermediate and final execution outputs
4. **AuditLog**: Complete audit trail with user actions and resource access
5. **ToolRegistry**: Dynamic tool management with versioning and categories
6. **ConfigurationVersion**: Specification versioning with checksums and rollback

### Relationships (Enforced by Prisma)
- Session → Many Executions (session_id foreign key)
- Execution → Many Results (execution_id foreign key)
- Session/Execution → Many AuditLogs (optional foreign keys)
- All entities use UUID primary keys with proper indexing

### Database Service Isolation ✅ **NEW**
- **Schema-Based Isolation**: PostgreSQL schemas for service separation (`agent_engine`, `auth_service`, etc.)
- **Connection String Pattern**: `postgresql://user:pass@host:port/postgres?schema=service_name`
- **Resource Sharing**: Multiple services share database instance while maintaining isolation
- **Migration Management**: Each service manages its own schema migrations

### Database Service Patterns
- **Connection Management**: Singleton service with connection pooling
- **CRUD Operations**: Type-safe operations via Prisma client
- **JSON Fields**: Flexible data storage for state, metadata, specifications
- **Health Monitoring**: Built-in health checks and statistics

## Dev UI Integration Architecture ✅ **NEW**

### Visual Development Interface
- **Browser-based testing**: http://localhost:8002 for interactive agent testing
- **Agent selection dropdown**: Dynamically populated from specs/agents/ directory
- **Events tab debugging**: Real-time trace logs with function call inspection
- **Multi-agent testing**: Switch between 6 example agents for comprehensive testing

### Dev UI Components
```
DevUILauncher
├── AgentDiscovery (YAML spec parsing)
├── DevUIConfiguration (port 8002, environment-aware)
├── Environment Setup (GEMINI_API_KEY validation)
└── ADK Integration (google.adk.agents import)
```

### Development Workflow Integration
- **One-command launch**: `make dev-ui` for immediate visual testing
- **Validation pipeline**: `make dev-ui-validate` for setup verification
- **Docker support**: `make dev-ui-docker` for containerized development
- **Agent discovery**: Automatic loading of all agents from specifications

### Port Configuration Strategy
- **Port 8002**: Configured throughout all components to avoid port 8000 conflicts
- **Environment awareness**: Dev UI adapts to development/staging/production contexts
- **Network integration**: tahoe-network Docker networking for service communication

## API Design Principles

### RESTful Endpoints
- Resource-based URLs
- Standard HTTP methods
- JSON request/response
- Consistent error format

### Endpoint Categories ✅ **IMPLEMENTED**
1. **Core**: Health, metrics, config
2. **Specifications**: Agent/workflow/tool specs, validation, composition (15 endpoints)
3. **Database**: Sessions, executions, results, audit logs, tools, configurations (15 endpoints)
4. **Configuration**: Hierarchical config management, runtime overrides, health (6 endpoints)
5. **Health**: ADK verification, database health, service statistics

## Security Architecture

### API Security
- Service token authentication
- Rate limiting per endpoint
- Input validation before processing
- Audit logging for all operations

### Configuration Security
- Sensitive values masked in logs
- Environment-based secrets
- No hardcoded credentials
- API keys via environment variables

## Performance Considerations

### Optimization Points
- Agent instance caching (LRU)
- Connection pooling (database, Redis)
- Async/await throughout
- Streaming for long operations

### Scalability Design
- Stateless service design
- Horizontal scaling ready
- Session state externalized
- Event-driven architecture

## Testing Strategy

### Test Levels
1. **Unit**: Component isolation
2. **Integration**: ADK integration
3. **E2E**: Complete workflows
4. **Performance**: Load and stress

### Coverage Requirements
- Minimum 80% code coverage
- All ADK integrations tested
- All API endpoints tested
- Critical paths have E2E tests

## Deployment Architecture

### Local Development
- **Docker Compose**: Multi-service infrastructure (PostgreSQL, Redis, Nginx)
- **Centralized .env**: Root-level environment file mounted in development
- **Hot Reload**: Source code volume mounting with auto-reload
- **Makefile Operations**: `make up`, `make logs`, `make test`, `make validate`

### Staging/Production
- **Environment Variables**: Configuration via Helm/Vault (no .env files)
- **Multi-stage Builds**: Optimized Docker images with security
- **Infrastructure Services**: External PostgreSQL, Redis, load balancers
- **Container Orchestration**: Kubernetes with Helm charts
- **Health Checks**: Built-in health and configuration endpoints

## Technical Decisions Made

### Language & Framework ✅ **IMPLEMENTED**
- **Python 3.12**: Using latest stable Python (ADK requires 3.9+)
- **FastAPI**: Async REST API framework with hierarchical configuration
- **Prisma ORM**: Type-safe database access with schema isolation
- **PostgreSQL 15**: Primary database with schema-based service isolation
- **Redis**: Caching and sessions with namespace-based isolation
- **Google ADK 1.10.0**: Core agent framework (validated and compliant)
- **Pydantic Settings**: Environment-aware hierarchical configuration management

### ADK Choices (Validated ✅)
- **InMemoryRunner**: Primary runner (not custom)
- **Automatic tool wrapping**: Default approach (explicit when needed)
- **Session services**: Use ADK's built-in InMemorySessionService
- **Naming Convention**: Python identifiers only (underscores, not hyphens)
- **Agent Architecture**: Separate instances for workflows, property access patterns

### Data Formats
- **YAML**: Primary specification format
- **JSON**: Alternative, API responses
- **Pydantic**: Data validation and configuration
- **Environment Variables**: Production configuration delivery

### Deployment & Infrastructure
- **Docker Compose**: Development with centralized .env mounting
- **Multi-stage Builds**: Production optimization and security
- **Kubernetes/Helm**: Staging and production orchestration
- **Vault Integration**: Secrets management for production

## Patterns to Avoid

### Anti-Patterns Identified (Real ADK v1.10.0 Validated)
1. **Don't use hyphens in agent names** (ADK validation error)
2. **Don't call session_service as method** (it's a property)
3. **Don't use `sub_agent` in LoopAgent** (use `sub_agents` list)
4. **Don't set model parameters directly in LlmAgent constructor** (use generate_content_config)
5. **Don't use fallback_models parameter** (not supported by real ADK LlmAgent)
6. **Don't pass custom parameters to workflow agents** (ParallelAgent, SequentialAgent, LoopAgent reject them)
7. **Don't reuse agent instances across workflows** (create separate instances)
8. Don't implement custom runners (use InMemoryRunner)
9. Don't manage sessions manually (use ADK services)
10. Don't hardcode business logic (use specifications)
11. Don't wrap simple functions (automatic wrapping preferred)
12. Don't create custom retry logic (ADK provides)

## Future Architecture Considerations

### Planned Enhancements
- Multi-model provider support (via LiteLLM)
- Vertex AI session backend
- Workflow marketplace
- Real-time collaboration
- Advanced monitoring dashboard

### Extension Points
- Custom agent types via BaseAgent inheritance (R2-T04 ✅)
- Tool marketplace integration
- Workflow template library
- Model provider plugins

## R2-T04: Custom Agents Architecture Patterns ✅

### Custom Agent Implementation Pattern
```python
class CustomAgent(BaseAgent):
    def __init__(self, name: str, custom_param: str = "default", **kwargs):
        # Initialize with only ADK BaseAgent fields
        super().__init__(
            name=name,
            **{k: v for k, v in kwargs.items() if k in ['parent_agent', 'before_agent_callback', 'after_agent_callback']}
        )
        
        # Store custom fields as instance attributes (not Pydantic fields)
        object.__setattr__(self, 'custom_param', custom_param)
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Custom implementation logic
        yield Event(type="result", data=self.custom_param)
```

### Key Architectural Decisions

1. **Pydantic BaseAgent Constraint Handling**
   - Real ADK BaseAgent is a Pydantic model with restricted field addition
   - Solution: Use `object.__setattr__` to bypass Pydantic validation for custom fields
   - Pattern ensures compatibility with ADK validation while enabling extension

2. **Custom Agent Registry System**
   - `UniversalAgentFactory.custom_registry` for dynamic class registration
   - Validation ensures inheritance from BaseAgent and `_run_async_impl` override
   - Supports both built-in Python classes and dynamic YAML-defined classes

3. **Specification-Driven Custom Agents**
   - Built-in agents: Direct Python class registration via `register_built_in_agents()`
   - Dynamic agents: YAML specifications with embedded `class_definition` sections
   - Seamless integration via `_build_custom_agent()` factory method

4. **Test Architecture for Real ADK**
   - No Mock objects for BaseAgent - real inheritance required
   - Test custom agents inherit from BaseAgent and implement `_run_async_impl`
   - MockSubAgent pattern for sub-agent testing with proper BaseAgent compliance

### Custom Agent Capabilities

1. **AdaptiveOrchestrator** - Dynamic orchestration patterns
   - Supports adaptive and sequential execution patterns
   - State-based agent selection logic
   - Configurable max iterations for execution control

2. **ConditionalRouter** - Condition-based routing
   - Safe condition evaluation with limited namespace
   - Supports basic property checks and complex expressions
   - Execution of first matching condition with fallback support

3. **StatefulWorkflow** - State management across executions
   - Persistent workflow state via session storage
   - Step-by-step execution with restart capabilities
   - Failure tracking and recovery mechanisms

4. **SimpleCounter** - Dynamic specification-based agent
   - Demonstrates YAML-embedded class definitions
   - Runtime class creation and registration
   - Example of fully specification-driven custom agents