# Project Tahoe - Architecture Decisions

## Core Architecture Patterns

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

### 2. Universal Agent Factory
**Pattern**: Single factory class creates all agent types from specifications
**Implementation**:
```python
class UniversalAgentFactory:
    def build_agent(spec: dict, context: dict) -> BaseAgent
```
**Supports**: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, Custom (BaseAgent)
**Features**:
- Automatic name sanitization (hyphens to underscores)
- Dynamic tool loading (registry, inline, import)
- Context injection for template variables
- Sub-agent composition with conditions

### 3. Centralized Configuration System
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

### 6. ADK Dev UI Integration Pattern ✅ **NEW**
**Pattern**: Visual development interface for agent testing and debugging
**Implementation**:
- DevUILauncher service with automatic agent discovery
- AgentDiscovery utility with YAML specification parsing
- Environment-aware configuration (port 8002, avoiding conflicts)
- One-command setup via Makefile targets
**Benefits**:
- Real-time visual agent testing and debugging
- Interactive development workflow with immediate feedback
- Browser-based interface with Events tab for trace inspection
- Foundation for R2 Composition visual validation

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

### Anti-Patterns Identified
1. **Don't use hyphens in agent names** (ADK validation error)
2. **Don't call session_service as method** (it's a property)
3. **Don't use `sub_agent` in LoopAgent** (use `sub_agents` list)
4. **Don't set model parameters in agent creation** (use runtime config)
5. **Don't reuse agent instances across workflows** (create separate instances)
6. Don't implement custom runners (use InMemoryRunner)
7. Don't manage sessions manually (use ADK services)
8. Don't hardcode business logic (use specifications)
9. Don't wrap simple functions (automatic wrapping preferred)
10. Don't create custom retry logic (ADK provides)

## Future Architecture Considerations

### Planned Enhancements
- Multi-model provider support (via LiteLLM)
- Vertex AI session backend
- Workflow marketplace
- Real-time collaboration
- Advanced monitoring dashboard

### Extension Points
- Custom agent types via BaseAgent
- Tool marketplace integration
- Workflow template library
- Model provider plugins