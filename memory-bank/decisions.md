# Project Tahoe - Key Decisions Log

## 2025-08-13: Task Structure Design

### Decision: Comprehensive YAML Task Files
**Choice**: Create highly detailed task files (~500 lines each) with complete implementation instructions
**Alternatives Considered**:
- Minimal task outlines (rejected - insufficient for autonomous execution)
- Markdown format (rejected - less structured than YAML)
- JSON format (rejected - less readable than YAML)
**Rationale**: 
- Future Claude Code sessions need complete context
- YAML provides structure with readability
- Detailed tasks reduce ambiguity during implementation
**Impact**: Higher upfront effort but smoother implementation phase

### Decision: R1 Foundation First
**Choice**: Complete all R1 Foundation tasks before other releases
**Alternatives Considered**:
- Parallel release development (rejected - dependencies unclear)
- Bottom-up from R7 (rejected - no foundation)
**Rationale**:
- Establishes development environment
- Verifies ADK integration early
- Creates patterns for subsequent tasks
**Impact**: Sequential but lower risk approach

### Decision: Task Validation Script
**Choice**: Python script to validate all task files
**Alternatives Considered**:
- Manual validation (rejected - error prone)
- GitHub Actions only (rejected - need local validation)
- JSON Schema validation (rejected - too rigid)
**Rationale**:
- Catches errors before implementation
- Ensures consistency across tasks
- Validates dependencies exist
**Impact**: Higher quality task files, fewer implementation issues

## 2025-08-13: ADK Integration Approach

### Decision: Use InMemoryRunner Exclusively
**Choice**: Standardize on InMemoryRunner for all agent execution
**Alternatives Considered**:
- Custom runner implementation (rejected - ADK advises against)
- Multiple runner types (rejected - unnecessary complexity)
**Rationale**:
- ADK documentation recommends this approach
- Provides all needed functionality
- Simpler to maintain
**Impact**: Consistent execution pattern throughout system

### Decision: Automatic Tool Wrapping Default
**Choice**: Use automatic function wrapping, FunctionTool only when needed
**Alternatives Considered**:
- Always use FunctionTool (rejected - unnecessary overhead)
- Custom tool wrapper (rejected - ADK handles this)
**Rationale**:
- ADK handles most cases automatically
- Reduces boilerplate code
- FunctionTool available for complex cases
**Impact**: Cleaner code, easier tool integration

### Decision: Specification-Driven Everything
**Choice**: All configuration via YAML/JSON specifications
**Alternatives Considered**:
- Code-based configuration (rejected - requires rebuilds)
- Database configuration (rejected - less transparent)
- Mixed approach (rejected - inconsistent)
**Rationale**:
- No code changes for new agents
- Version control friendly
- Clear audit trail
**Impact**: More flexible system, easier to modify

## 2025-08-13: Project Structure

### Decision: Monorepo Architecture
**Choice**: Single repository with services directory
**Alternatives Considered**:
- Multiple repositories (rejected - harder to coordinate)
- Flat structure (rejected - less organized)
**Rationale**:
- Easier dependency management
- Simplified deployment
- Better code sharing
**Impact**: All code in one place, simpler CI/CD

### Decision: Tasks Directory at Root
**Choice**: Place tasks/ directory at repository root
**Alternatives Considered**:
- Inside docs/ (rejected - tasks are executable)
- Inside each service (rejected - tasks span services)
- Separate repo (rejected - needs to be with code)
**Rationale**:
- Tasks are project-wide, not service-specific
- Easy to find and access
- Clear separation from implementation
**Impact**: Clear task organization, easy navigation

## 2025-08-13: Technology Stack

### Decision: FastAPI for REST API
**Choice**: FastAPI as the web framework
**Alternatives Considered**:
- Flask (rejected - less async support)
- Django (rejected - too heavyweight)
- aiohttp (rejected - less features)
**Rationale**:
- Native async support
- Automatic API documentation
- Pydantic integration
- Modern and performant
**Impact**: Better performance, automatic docs

### Decision: Prisma ORM
**Choice**: Prisma for database access
**Alternatives Considered**:
- SQLAlchemy (rejected - less type safety)
- Raw SQL (rejected - more error prone)
- Django ORM (rejected - tied to Django)
**Rationale**:
- Type-safe database access
- Good migration support
- Modern approach
**Impact**: Safer database operations, better DX

### Decision: PostgreSQL Database
**Choice**: PostgreSQL as primary database
**Alternatives Considered**:
- MySQL (rejected - less features)
- MongoDB (rejected - less suitable for relational data)
- SQLite (rejected - not production ready)
**Rationale**:
- Robust and reliable
- JSON support for flexible data
- Good performance
**Impact**: Solid foundation for data storage

## 2025-08-13: Development Process

### Decision: Test-Driven Development
**Choice**: Write tests before implementation
**Alternatives Considered**:
- Tests after implementation (rejected - more bugs)
- No formal testing (rejected - too risky)
**Rationale**:
- Catches issues early
- Documents expected behavior
- Ensures code works as designed
**Impact**: Higher quality code, fewer bugs

### Decision: 80% Test Coverage Minimum
**Choice**: Require 80% code coverage
**Alternatives Considered**:
- 100% coverage (rejected - diminishing returns)
- 60% coverage (rejected - too low)
- No requirement (rejected - inconsistent quality)
**Rationale**:
- Balances quality with effort
- Industry standard
- Achievable target
**Impact**: Good test coverage without perfectionism

## 2025-08-13 (Evening): Implementation Decisions

### Decision: Python 3.12 for Development
**Choice**: Use Python 3.12 (latest stable)
**Alternatives Considered**:
- Python 3.9 (rejected - older version)
- Python 3.11 (rejected - not latest)
**Rationale**:
- ADK supports 3.9+, so 3.12 is compatible
- Latest features and performance improvements
- Better type hints and error messages
**Impact**: Modern Python features available

### Decision: Docker Compose for Local Infrastructure
**Choice**: Use docker-compose.yml for postgres and redis
**Alternatives Considered**:
- Manual service installation (rejected - inconsistent)
- Kubernetes locally (rejected - overkill)
**Rationale**:
- Easy to start/stop services
- Consistent across environments
- Simple configuration
**Impact**: Simplified local development

## 2025-08-13 (ADK/Config Session): Critical Architecture Decisions

### Decision: ADK Pattern Validation Required
**Choice**: Validate all ADK usage against official documentation patterns
**Alternatives Considered**:
- Trial-and-error development (rejected - led to multiple errors)
- Minimal validation (rejected - production issues)
**Rationale**:
- ADK has specific requirements that must be followed exactly
- Validation prevents production issues
- Establishes patterns for all future development
**Impact**: Production-ready code from the start, avoids debugging later

### Decision: Centralized Configuration Architecture
**Choice**: Environment-aware configuration with single root .env file for development
**Alternatives Considered**:
- Service-level .env files (rejected - configuration sprawl)
- Database configuration (rejected - bootstrap problems)
- Hard-coded configuration (rejected - not environment-flexible)
**Rationale**:
- Supports development (.env) and production (Helm/Vault) patterns
- Centralized management reduces configuration drift
- Pydantic Settings provides validation and type safety
**Impact**: Consistent configuration across all services and environments

### Decision: Docker Multi-stage Production Builds
**Choice**: Use multi-stage Dockerfile with production optimization
**Alternatives Considered**:
- Single-stage development builds (rejected - security issues)
- No Docker (rejected - environment inconsistency)
**Rationale**:
- Smaller production images
- Better security (non-root user, minimal dependencies)
- Separates build and runtime concerns
**Impact**: Production-ready containers with security best practices

### Decision: ADK Anti-pattern Documentation
**Choice**: Document all discovered ADK anti-patterns to prevent future errors
**Alternatives Considered**:
- Fix and forget (rejected - errors will repeat)
- Minimal documentation (rejected - insufficient guidance)
**Rationale**:
- ADK patterns are not intuitive and must be learned
- Team knowledge base prevents repeated mistakes
- Enables faster development for new team members
**Impact**: Faster development, fewer ADK-related bugs

## 2025-08-13: Database Architecture Decisions

### Decision: Prisma ORM for Database Access
**Choice**: Use Prisma ORM with PostgreSQL for all database operations
**Alternatives Considered**:
- SQLAlchemy (rejected - less type safety, more complex)
- Raw SQL with asyncpg (rejected - more error prone, no migrations)
- Django ORM (rejected - tied to Django framework)
**Rationale**:
- Type-safe database access with automatic Python client generation
- Built-in migration system with version control
- JSON field support for flexible data storage (specifications, state)
- Modern developer experience with schema-first approach
**Impact**: Safer database operations, automatic type checking, easier maintenance

### Decision: Comprehensive Database Schema Design
**Choice**: Create 6 core entities covering all platform operations
**Alternatives Considered**:
- Minimal schema with just sessions (rejected - insufficient for production)
- NoSQL document store (rejected - relational data needs)
- Separate databases per service (rejected - unnecessary complexity for now)
**Rationale**:
- Session tracking required for ADK integration
- Execution tracking needed for observability and debugging
- Audit logging essential for security and compliance
- Tool registry enables dynamic tool management
- Configuration versioning supports rollback and change tracking
**Impact**: Complete operational visibility, production-ready audit capabilities

### Decision: UUID Primary Keys with Proper Indexing
**Choice**: Use UUIDs for all primary keys with strategic indexing
**Alternatives Considered**:
- Auto-incrementing integers (rejected - not globally unique)
- Composite keys (rejected - more complex relationships)
**Rationale**:
- Globally unique identifiers across distributed systems
- No collision risk when scaling horizontally
- Better security (non-guessable IDs)
- Proper indexes on foreign keys and query patterns
**Impact**: Scalable ID scheme, better security, optimal query performance

### Decision: Database Service Singleton Pattern
**Choice**: Single DatabaseService instance with connection management
**Alternatives Considered**:
- New connection per request (rejected - performance overhead)
- Global connection pool (rejected - less controlled)
- Per-endpoint database clients (rejected - inconsistent)
**Rationale**:
- Consistent connection management across the application
- Built-in health checking and error handling
- Proper async/await support with Prisma client
- Easy to test and mock for unit tests
**Impact**: Reliable database access, consistent error handling, testable code

## 2025-08-13: Configuration Architecture Decisions

### Decision: Database Schema Isolation vs Separate Databases
**Choice**: Use PostgreSQL schemas for service isolation instead of separate databases
**Alternatives Considered**:
- Separate databases per service (rejected - resource overhead)
- Single shared database with table prefixes (rejected - less isolation)
- NoSQL document stores (rejected - relational data needs)
**Rationale**:
- Better resource utilization (shared connection pools, memory)
- Proper service isolation with schema boundaries
- Easier backup and maintenance operations
- PostgreSQL schemas provide strong isolation guarantees
**Impact**: Efficient multi-service architecture with clear boundaries

### Decision: Redis Namespace Pattern for Service Isolation
**Choice**: Use Redis namespaces (key prefixes) for service isolation
**Alternatives Considered**:
- Separate Redis databases (rejected - limited to 16 databases)
- Separate Redis instances (rejected - resource overhead)
- No isolation (rejected - key conflicts between services)
**Rationale**:
- Unlimited logical separation within single Redis instance
- Clear key ownership and debugging
- Easy to implement and maintain
- Supports complex namespace hierarchies
**Impact**: Clean service isolation with efficient resource usage

### Decision: Hierarchical Configuration System
**Choice**: Three-level configuration hierarchy (base → environment → runtime)
**Alternatives Considered**:
- Single configuration file (rejected - not environment-flexible)
- Database-stored configuration (rejected - bootstrap problems)
- Code-based configuration (rejected - requires rebuilds)
**Rationale**:
- Environment-specific deployment patterns
- Runtime configuration changes without code deployment
- Clear precedence rules for configuration values
- Supports both development and production workflows
**Impact**: Flexible configuration management with clear override patterns

### Decision: Service Discovery URL Generation
**Choice**: Environment-aware service URL generation in configuration
**Alternatives Considered**:
- Hardcoded service URLs (rejected - not environment-flexible)
- External service discovery (rejected - adds complexity)
- DNS-based discovery only (rejected - development issues)
**Rationale**:
- Supports development (localhost), staging, and production patterns
- Simple implementation with clear patterns
- Easy to test and debug
- Follows environment isolation principles
**Impact**: Seamless service communication across all environments

### Decision: Configuration Security Pattern
**Choice**: Sensitive value masking by default in all APIs and exports
**Alternatives Considered**:
- No masking (rejected - security risk)
- Opt-in masking (rejected - likely to be forgotten)
- Complete hiding (rejected - debugging difficulties)
**Rationale**:
- Security by default approach
- Debugging still possible with explicit flags
- Consistent across all configuration endpoints
- Prevents accidental exposure in logs and exports
**Impact**: Secure configuration management with debugging capabilities

## 2025-08-13: ADK Dev UI Integration Decisions

### Decision: Port 8002 for Dev UI
**Choice**: Use port 8002 for ADK Dev UI instead of default 8000
**Alternatives Considered**:
- Port 8000 (rejected - already in use by unrelated project)
- Port 8001 (rejected - used by agent-engine service)
- Random available port (rejected - harder to remember and document)
**Rationale**:
- Port 8000 was explicitly unavailable due to existing project conflict
- Port 8002 follows logical sequence (8001 for agent-engine, 8002 for dev-ui)
- Easy to remember and document
- No known conflicts in development environment
**Impact**: Clean port separation enabling parallel development of agent-engine and visual testing

### Decision: Visual Development as Foundation for R2
**Choice**: Implement Dev UI integration as R2-T00 before other R2 Composition tasks
**Alternatives Considered**:
- Implement Dev UI after R2 Composition (rejected - no visual validation during development)
- Skip Dev UI entirely (rejected - makes agent testing much harder)
- Basic command-line testing only (rejected - less developer-friendly)
**Rationale**:
- Visual interface enables immediate feedback during agent development
- Events tab provides critical debugging capabilities for complex agents
- Browser-based testing more accessible for team collaboration
- Establishes pattern for visual validation of all R2 components
**Impact**: Faster R2 development with immediate visual feedback and debugging

### Decision: Comprehensive Example Agent Set
**Choice**: Create 6 diverse example agents for Dev UI testing
**Alternatives Considered**:
- Single simple agent (rejected - insufficient for testing variety)
- Complex single agent (rejected - harder to understand and debug)
- No example agents (rejected - nothing to test Dev UI with)
**Rationale**:
- Different agent types test various Dev UI capabilities
- Tools in agents demonstrate function call debugging
- Variety enables comprehensive testing of agent discovery and selection
- Examples serve as templates for future agent development
**Impact**: Rich testing environment that validates Dev UI functionality and provides development templates

### Decision: Agent Discovery via Specification Parsing
**Choice**: Use existing SpecificationParser to discover agents from YAML files
**Alternatives Considered**:
- Hardcoded agent list (rejected - not dynamic)
- Separate discovery mechanism (rejected - duplicates existing parsing logic)
- Database-based discovery (rejected - adds unnecessary complexity)
**Rationale**:
- Leverages existing, tested specification parsing infrastructure
- Maintains consistency with specification-driven architecture
- Automatic discovery as new agents are added to specs/agents/
- Validates that specification parsing works correctly
**Impact**: Seamless integration with existing architecture and automatic scaling with new agents

### Decision: Docker Support for Dev UI
**Choice**: Create specialized Docker configuration for Dev UI alongside local development
**Alternatives Considered**:
- Local development only (rejected - inconsistent with project Docker patterns)
- Integrate into existing docker-compose (rejected - Dev UI is optional)
- Separate Docker setup entirely (rejected - harder to coordinate)
**Rationale**:
- Maintains consistency with Docker-based development patterns
- Optional Dev UI service doesn't affect core infrastructure
- Enables containerized testing in CI/CD environments
- Provides isolation for Dev UI dependencies
**Impact**: Flexible development options supporting both local and containerized workflows

### Decision: Service-Only Operation for Dev UI
**Choice**: Dev UI operates entirely within agent-engine service directory, no root-level dependencies
**Alternatives Considered**:
- Root-level operation (rejected - conflicts with service independence principle)
- Mixed root/service operation (rejected - confusing and inconsistent)
- Service operation with root fallback (rejected - maintains unwanted coupling)
**Rationale**:
- Aligns with monorepo service autonomy principle
- Each service operates independently with their own docker setup
- Consistent with removal of root-level Makefile and docker-compose
- Clear separation of concerns - Dev UI is agent-engine specific
- Eliminates confusion about where commands should be run
**Impact**: Clear service boundaries, consistent architecture, easier service deployment

## Future Decisions Needed

### Pending: CI/CD Pipeline
- GitHub Actions vs GitLab CI vs Jenkins
- Deployment strategy (blue-green, canary, rolling)
- Container registry choice

### Pending: Monitoring Solution
- Prometheus + Grafana vs DataDog vs New Relic
- Log aggregation strategy
- APM tool selection

### Pending: Authentication Method
- JWT vs OAuth2 vs API Keys
- Session management approach
- Authorization strategy (RBAC vs ABAC)

### Pending: Model Provider Strategy
- Gemini-only vs multi-provider
- Fallback strategies
- Cost optimization approach

## Decision Framework

### Criteria for Technical Decisions
1. **Alignment with ADK**: Does it follow ADK patterns?
2. **Simplicity**: Is it the simplest solution that works?
3. **Maintainability**: Can it be easily maintained?
4. **Performance**: Does it meet performance requirements?
5. **Flexibility**: Does it allow for future changes?

### Decision Process
1. Identify the problem/need
2. List alternatives
3. Evaluate against criteria
4. Document choice and rationale
5. Implement and validate
6. Review and adjust if needed