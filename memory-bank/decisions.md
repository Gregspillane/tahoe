# Project Tahoe - Key Decisions Log

## 2025-08-13: R2 Task Validation (Evening - Session 3)

### Decision: Validate Tasks Against MASTERPLAN Before Implementation
**Context**: R2-T1 task specification had several misalignments with MASTERPLAN
**Decision**: Thoroughly validate each task against MASTERPLAN before implementation
**Rationale**:
- Original task specs were created before full MASTERPLAN was complete
- MASTERPLAN contains critical implementation details not in original tasks
- Validation prevents rework and ensures correct architecture
- Stub classes maintain proper interfaces for future integration
**Impact**: R2-T1 corrected, other R2 tasks should be validated before implementation

### Decision: Use Stub Classes Instead of Pure Mocks
**Context**: R2-T1 needed placeholder implementations for AgentFactory and ResultAggregator
**Decision**: Create stub classes with proper interfaces rather than inline mocks
**Rationale**:
- Maintains correct interface contracts from the start
- Easier to replace with real implementations later
- Prevents interface drift between components
- Better testing and validation
**Impact**: Created stub implementations for AgentFactory and ResultAggregator

### Decision: Include ADK Imports From Start
**Context**: Original task delayed ADK integration until later
**Decision**: Import ADK classes even when using mock implementations
**Rationale**:
- MASTERPLAN shows ADK as core dependency from line 309
- Maintains correct import structure
- Prevents major refactoring later
- ADK interfaces guide mock implementations
**Impact**: All orchestrator code will use proper ADK imports

## 2025-08-13: R1-T3 API Implementation (Evening - Session 2)

### Decision: Orchestrator Skeleton Pattern
**Context**: Need to implement API endpoints before full orchestration logic
**Decision**: Created orchestrator as skeleton class with mock results
**Rationale**:
- Allows API testing without complex agent logic
- Establishes interface contract early
- Enables incremental development
- Returns realistic mock data for testing
**Impact**: Full orchestration deferred to R2, API fully functional now

### Decision: Comprehensive Endpoint Coverage
**Context**: R1-T3 originally had basic endpoints, masterplan had more
**Decision**: Implemented all masterplan endpoints in R1-T3
**Rationale**:
- Complete API surface even in foundation phase
- Easier to test integration points
- Status and metrics endpoints valuable immediately
**Impact**: R1-T3 now includes status, metrics, and full CRUD operations

## 2025-08-13: Task Alignment Updates (Evening - Session 1)

### Decision: Standardize on Port 8001
**Context**: MASTERPLAN had inconsistent references to port 8000 vs 8001
**Decision**: Updated all references to use port 8001 consistently
**Rationale**:
- Port 8001 avoids more common conflicts
- Already established in task specifications
- Consistent with infrastructure decisions
**Impact**: MASTERPLAN.md updated throughout, all tasks use 8001

### Decision: Enhance R1-T3 Task Specification
**Context**: R1-T3 task was missing some endpoints from masterplan
**Decision**: Added /status/analysis/{id}, PUT /agents/templates/{id}, and /metrics endpoints
**Rationale**:
- Complete API surface even in foundation phase
- Status endpoint useful for monitoring
- Metrics endpoint helps with observability
**Impact**: R1-T3 now includes all masterplan endpoints

## 2025-08-13: Database Implementation Session (Evening)

### Decision: Infrastructure as Separate Service
**Context**: Discussion about where PostgreSQL and Redis should live
**Decision**: Created `/services/infrastructure/` with shared PostgreSQL and Redis
**Rationale**:
- Single PostgreSQL instance with multiple schemas is more efficient
- Single Redis instance with namespaced keys reduces overhead
- Easier backups, monitoring, and management
- Matches production architecture (RDS + ElastiCache)
**Impact**: All services connect to shared infrastructure, not embedded databases

### Decision: Prisma with Computed Config Fields
**Context**: Config management needs both component values and computed URLs
**Decision**: Use Pydantic computed fields for DATABASE_URL and REDIS_URL
**Rationale**:
- Components (host, port, user) configurable individually
- URLs computed from components
- Flexibility for different environments
**Impact**: DATABASE_URL must be exported separately for Prisma CLI

### Decision: Enhanced Config.py
**Context**: Need environment-aware configuration
**Decision**: Added computed fields for service URLs, CORS, debug mode
**Rationale**:
- Service URLs change based on environment (dev/staging/prod)
- CORS origins computed based on environment
- Debug mode automatic in development
**Impact**: More intelligent configuration with less manual setup

## 2025-08-13: Implementation Session (Afternoon)

### Decision: Infrastructure as Service
**Context**: Needed to organize infrastructure in monorepo
**Decision**: Moved infrastructure to `/services/infrastructure/`
**Rationale**: 
- Consistent with monorepo pattern where everything is a service
- Each service (including infrastructure) can have its own DNS
- Cleaner organization
**Impact**: Infrastructure docker-compose moved from root to services folder

### Decision: Port 8001 is Correct
**Context**: Discrepancy between masterplan (8000) and task spec (8001)
**Decision**: Keep port 8001 as specified in tasks
**Rationale**:
- Task specifications are the execution plan
- Port 8001 avoids more conflicts
- Updated CLAUDE.md to reflect correct port
**Impact**: All configurations use port 8001

### Decision: Flexible Dependency Versioning
**Context**: FastAPI and google-adk had Starlette version conflicts
**Decision**: Use >= instead of pinned versions in requirements.txt
**Rationale**:
- Allows pip to resolve compatible versions
- More flexible for future updates
- Avoids manual version management
**Impact**: Dependencies can float to compatible versions

## 2025-08-13: Task Planning Session (Morning)

### Decision: Port Configuration Change
**Context**: Discovered port conflicts with existing local services
**Decision**: Changed default ports to avoid conflicts
- PostgreSQL: 5432 → 5435
- Redis: 6379 → 6382
- API: 8000 → 8001
**Rationale**: Allow parallel development without stopping other services
**Impact**: All task specifications and documentation updated

### Decision: Task Specification Format
**Context**: Need executable specifications for Claude Code
**Decision**: Created YAML-based task specifications with structured format
**Rationale**: 
- YAML provides clear structure and readability
- Each task fits in single Claude Code session
- Includes validation steps for autonomous verification
**Impact**: 10 task files created with consistent structure

### Decision: Release Structure
**Context**: Need to organize development into manageable phases
**Decision**: Three releases (R1 Foundation, R2 Orchestration, R3 Specialists)
**Rationale**:
- Progressive complexity building
- Each release provides working functionality
- Dependencies clearly defined
**Impact**: Clear development sequence established

### Decision: Shared Context Document
**Context**: Tasks need consistent patterns and configurations
**Decision**: Created shared project-context.md for all tasks
**Rationale**:
- Single source of truth for patterns
- Reduces repetition in task files
- Maintains consistency across implementations
**Impact**: All tasks reference shared context

## Previous Decisions (from Planning Phase)

### Decision: Monorepo Structure
**Context**: Multiple interconnected services planned
**Decision**: Use monorepo with services/ directory
**Rationale**:
- Easier coordination during development
- Shared infrastructure configuration
- Simplified local development
**Impact**: All services under single repository

### Decision: Database-First Architecture
**Context**: Need flexible agent configuration
**Decision**: Store all configurations in PostgreSQL
**Rationale**:
- Runtime configuration without code changes
- Business logic in database
- Easier updates and testing
**Impact**: Service reads configurations dynamically

### Decision: Google ADK for Agents
**Context**: Need robust agent framework
**Decision**: Use Google ADK as primary agent framework
**Rationale**:
- Production-ready framework
- Good Python support
- Flexible tool integration
**Impact**: Core dependency for agent implementation

### Decision: Service Independence
**Context**: Planning for multiple services
**Decision**: Each service completely self-contained
**Rationale**:
- Independent deployment possible
- Clear service boundaries
- Easier testing and development
**Impact**: No shared code between services

### Decision: KISS Principle
**Context**: Risk of over-engineering
**Decision**: Explicitly follow Keep It Simple principle
**Rationale**:
- Faster initial development
- Easier debugging
- Clear implementation path
**Impact**: All tasks emphasize simplicity

## Task Implementation Guidelines

### Decision: Session-Sized Tasks
**Context**: Claude Code context limitations
**Decision**: Each task fits in one development session
**Rationale**:
- Manageable scope per session
- Clear completion criteria
- Reduces context switching
**Impact**: Tasks broken into 10 discrete units

### Decision: Local-First Development
**Context**: Need to validate before deployment
**Decision**: Everything works in Docker Compose first
**Rationale**:
- Immediate feedback
- No external dependencies
- Simplified debugging
**Impact**: All tasks include local validation

### Decision: Mock-First Testing
**Context**: External API dependencies expensive
**Decision**: Use mocks for initial development
**Rationale**:
- Faster development cycles
- No API costs during development
- Predictable test results
**Impact**: Mock implementations in early tasks