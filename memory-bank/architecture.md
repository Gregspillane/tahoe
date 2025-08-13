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

### 3. Hierarchical Configuration
**Pattern**: Base → Environment → Runtime override hierarchy
**Implementation**:
- Base: `.env` file
- Environment: `config/{environment}.env`
- Runtime: Specification overrides
**Loading Order**: Base values overridden by environment, both overridden by runtime

### 4. Plugin-Based Tool System
**Pattern**: Runtime tool registration with dynamic loading
**Implementation**:
- Tool registry with validation
- Automatic function wrapping (ADK feature)
- Explicit FunctionTool when needed
**Categories**: Analysis, Generation, Integration, Utility

## ADK Integration Points

### Agent Creation
- **LlmAgent**: Primary agent type for LLM interactions
- **Workflow Agents**: Sequential, Parallel, Loop for orchestration
- **BaseAgent**: Extension point for custom agents

### Execution Runtime
- **InMemoryRunner**: Primary execution component
- Methods: `run()` for sync, `run_async()` for streaming
- Session management built-in

### Session Management
- **InMemorySessionService**: Default session backend
- **Custom Backends**: Redis, Vertex AI (planned)
- Session state persistence and recovery

### Tool Integration
- **Automatic Wrapping**: Most Python functions work directly
- **FunctionTool**: Explicit wrapping for complex tools
- **Built-in Tools**: google_search and others from ADK

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

## Database Schema Design

### Core Entities
1. **Session**: ADK session tracking
2. **Execution**: Workflow/agent execution records
3. **Result**: Execution outputs
4. **AuditLog**: Complete audit trail
5. **ToolRegistry**: Dynamic tool management
6. **ConfigurationVersion**: Specification versioning

### Relationships
- Session → Many Executions
- Execution → Many Results
- All entities → Audit logs

## API Design Principles

### RESTful Endpoints
- Resource-based URLs
- Standard HTTP methods
- JSON request/response
- Consistent error format

### Endpoint Categories
1. **Core**: Health, metrics, config
2. **Agents**: Composition, management
3. **Workflows**: Execution, monitoring
4. **Tools**: Registration, discovery
5. **Sessions**: Creation, state management

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
- Docker Compose for infrastructure
- Virtual environment for Python
- Hot reload for development

### Production (Future)
- AWS EKS for orchestration
- HashiCorp Vault for secrets
- Multi-region deployment
- Blue-green deployments

## Technical Decisions Made

### Language & Framework
- **Python 3.12**: Using latest stable Python (ADK requires 3.9+)
- **FastAPI**: Async REST API framework
- **Prisma**: Type-safe ORM
- **Redis**: Caching and sessions
- **Google ADK 1.10.0**: Core agent framework

### ADK Choices
- **InMemoryRunner**: Primary runner (not custom)
- **Automatic tool wrapping**: Default approach
- **Session services**: Use ADK's built-in

### Data Formats
- **YAML**: Primary specification format
- **JSON**: Alternative, API responses
- **Pydantic**: Data validation

## Patterns to Avoid

### Anti-Patterns Identified
1. Don't implement custom runners (use InMemoryRunner)
2. Don't manage sessions manually (use ADK services)
3. Don't hardcode business logic (use specifications)
4. Don't wrap simple functions (automatic wrapping)
5. Don't create custom retry logic (ADK provides)

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