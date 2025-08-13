# Project Tahoe - Architecture Decisions

## Core Architecture Patterns

### Service Architecture (Updated 2025-08-13 Evening)
- **Monorepo Structure**: Services organized under `/services/` directory
- **Service Independence**: Each service completely self-contained
- **Shared Infrastructure**: PostgreSQL and Redis run as separate infrastructure services
- **Database Isolation**: Single PostgreSQL instance with service-specific schemas
- **Cache Namespacing**: Single Redis instance with namespaced keys
- **Connection Pattern**: Services connect to infrastructure via host machine ports

### Agent-Engine Service Patterns

#### Port Configuration (Updated 2025-08-13)
- **API Port**: 8001 (avoids conflict with other services)
- **PostgreSQL Port**: 5435 (dedicated instance)
- **Redis Port**: 6382 (dedicated instance)

#### Database-First Design
- All business logic stored in PostgreSQL
- Configuration-driven agent behavior
- Dynamic workflow execution from database templates
- Prisma ORM for type-safe database access

#### Stateless Execution
- No internal state in service
- PostgreSQL for persistent storage
- Redis for transient caching and sessions
- All state externalized and recoverable

#### Agent Framework (Updated 2025-08-13 Late Evening - ADK Verified)
- **Core Classes**: LlmAgent (not Agent), ParallelAgent, SequentialAgent
- **Execution Pattern**: Runner with InMemorySessionService for agent execution
- **Tool Integration**: FunctionTool wrapper (not @tool decorator)
- **Event Processing**: Extract results from runner.run_async() events
- AgentFactory pattern for dynamic agent instantiation from database templates
- TahoeAgent wrapper providing standardized AgentResult format
- Real-time template loading with Redis caching (5-minute TTL)
- Multi-provider model support (Gemini, OpenAI, Anthropic)
- Comprehensive error handling and fallback patterns
- ResultAggregator with weighted scoring and business rules
- Google Gemini API integrated and tested

### Technical Stack (Validated 2025-08-13 Evening)
- **Language**: Python 3.11
- **API Framework**: FastAPI with Uvicorn
- **Agent Framework**: Google ADK (v1.10.0+)
- **ORM**: Prisma for Python (v0.15.0)
- **Cache**: Redis with TTL management
- **Container**: Docker with Docker Compose
- **Dependency Management**: Flexible versioning (>=) to avoid conflicts
- **Configuration**: Pydantic Settings with computed fields

### Caching Strategy
```
agent:template:{id}     # TTL: 5 minutes
scorecard:{id}          # TTL: 5 minutes
portfolio:{id}          # TTL: 10 minutes
analysis:session:{id}   # TTL: 30 minutes
```

### Agent Orchestration Flow
1. Content Analysis → Determine requirements
2. Agent Selection → Based on scorecard rules
3. Execution Planning → Parallel/sequential groups
4. Agent Execution → With timeout management
5. Result Aggregation → Weighted scoring
6. Persistence → Store in PostgreSQL

### Model Provider Architecture
- Multi-provider support (Gemini, OpenAI, Anthropic)
- Provider-agnostic interface
- Configuration per model
- Fallback handling
- Environment-based API keys

### API Design
- RESTful endpoints
- Service token authentication
- Comprehensive error handling
- Health checks with dependency validation
- Swagger documentation auto-generated

### Testing Architecture
- Unit tests for isolated components
- Integration tests for workflows
- Local validation in Docker Compose
- Fixture-based test data
- Mock providers for testing

## Integration Points

### Infrastructure Services (Shared)
- **PostgreSQL**: Port 5435
  - `agent_engine` schema for agent-engine service
  - `auth` schema for future auth service
  - `billing` schema for future billing service
- **Redis**: Port 6382
  - `agent-engine:*` namespace for agent-engine
  - `auth:*` namespace for auth service
  - `billing:*` namespace for billing service

### Service Communication
- **Local Development**: Direct connection via localhost ports
- **Docker Environment**: Connection via host.docker.internal
- **Production**: Connection via internal network or managed services

### Internal Components (agent-engine) (Updated 2025-08-13 Evening)
- Orchestrator ↔ AgentFactory (real ADK integration)
- AgentFactory ↔ ModelRegistry (static configuration)
- AgentFactory ↔ ToolRegistry (placeholder tools)
- TahoeAgent ↔ Google ADK LlmAgent (production ready)
- Orchestrator ↔ Result Aggregator (AgentResult processing)
- All components → Database via Prisma
- All components → Cache via Redis (5-minute template TTL)

## Security Patterns
- Service token authentication
- Environment variable configuration
- No hardcoded secrets
- Database connection pooling
- Redis password protection

## Development Patterns
- KISS principle throughout
- Incremental development
- Session-sized tasks
- Local-first development
- Configuration over code

## Configuration Management (Added 2025-08-13 Evening)
- Centralized .env at monorepo root
- Environment-specific overrides in /config/{env}.env
- Service-specific prefixes for variables
- dotenv loading before pydantic settings
- Single source of truth for all services

## Scalability Considerations
- Stateless service design
- Horizontal scaling ready
- Cache-first performance
- Async execution patterns
- Database connection pooling