# Project Tahoe - Architecture Decisions

## Core Architecture Patterns

### Service Architecture (Updated 2025-08-13)
- **Monorepo Structure**: Services organized under `/services/` directory
- **Service Independence**: Each service completely self-contained
- **Infrastructure as Service**: Infrastructure moved to `/services/infrastructure/`
- **Database Isolation**: Shared PostgreSQL with service-specific schemas
- **Cache Namespacing**: Shared Redis with namespaced keys

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

#### Agent Framework
- Google ADK as core agent framework
- Database-driven agent instantiation
- Standardized agent result format
- Factory pattern for agent creation

### Technical Stack (Validated 2025-08-13)
- **Language**: Python 3.11
- **API Framework**: FastAPI with Uvicorn
- **Agent Framework**: Google ADK (v1.10.0+)
- **ORM**: Prisma for Python
- **Cache**: Redis with TTL management
- **Container**: Docker with Docker Compose
- **Dependency Management**: Flexible versioning (>=) to avoid conflicts

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

### External Services
- **PostgreSQL**: Port 5435, agent_engine schema
- **Redis**: Port 6382, agent-engine:* namespace
- **Model Providers**: Via API keys in environment

### Internal Components
- Orchestrator ↔ Agent Factory
- Agent Factory ↔ Model Registry
- Orchestrator ↔ Result Aggregator
- All components → Database via Prisma
- All components → Cache via Redis

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

## Scalability Considerations
- Stateless service design
- Horizontal scaling ready
- Cache-first performance
- Async execution patterns
- Database connection pooling