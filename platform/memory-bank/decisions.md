# Platform Service Technical Decisions

## Database Architecture Decisions

### Decision: Shared Database with Table Coexistence
**Date**: August 15, 2025  
**Context**: Platform service needs to integrate with existing transcription service infrastructure.

**Decision**: Use the existing shared `tahoe` PostgreSQL database with platform-specific table prefixes.

**Rationale**:
- **Infrastructure Simplicity**: Leverages existing database setup
- **Data Consistency**: Enables cross-service data relationships
- **Operational Efficiency**: Single database to manage and backup
- **Cost Effectiveness**: No additional database infrastructure needed

**Implementation**:
- Platform tables use descriptive names (e.g., `tenants`, `users`, `api_keys`)
- Transcription service tables remain unchanged
- Prisma schema designed to coexist without conflicts
- Used `prisma db push` instead of migrations to avoid schema conflicts

**Trade-offs**:
-  Simplified infrastructure and operations
-  Easier data relationships between services
-   Potential schema migration coordination needed
-   Single point of failure for all services

### Decision: Row-Level Tenant Isolation
**Date**: August 15, 2025  
**Context**: Multi-tenant SaaS requires strong data isolation.

**Decision**: Implement tenant isolation using `tenant_id` columns on all tables with repository-level filtering.

**Rationale**:
- **Security**: Prevents cross-tenant data access
- **Performance**: More efficient than database-per-tenant
- **Simplicity**: Single database with automatic filtering
- **Flexibility**: Easier to implement cross-tenant analytics

**Implementation**:
- Every data table includes `tenant_id` foreign key
- Repository pattern enforces automatic tenant filtering
- TypeScript types include tenant context
- Database indexes on `tenant_id` for performance

**Alternative Considered**: Database-per-tenant
- **Rejected**: Too complex for current scale, operational overhead

---

## Container & Infrastructure Decisions

### Decision: Alpine Linux with OpenSSL Dependencies
**Date**: August 15, 2025  
**Context**: Prisma requires OpenSSL libraries that Alpine Linux doesn't include by default.

**Decision**: Use `node:18-alpine` base image with additional `openssl libc6-compat` packages.

**Problem Encountered**:
```
Error loading shared library libssl.so.1.1: No such file or directory
```

**Solution Applied**:
```dockerfile
FROM node:18-alpine
RUN apk add --no-cache openssl libc6-compat
```

**Rationale**:
- **Size**: Alpine provides smaller container images
- **Compatibility**: Additional packages solve Prisma dependencies
- **Security**: Regular Alpine security updates
- **Performance**: Faster container startup times

**Alternative Considered**: Ubuntu-based Node image
- **Rejected**: Larger image size, slower builds

### Decision: Port 9200 for Platform Service
**Date**: August 15, 2025  
**Context**: Need consistent port allocation across Tahoe services.

**Decision**: Allocate port 9200 to platform service following established pattern.

**Rationale**:
- **Consistency**: Follows Tahoe port pattern (transcription on 9100)
- **Non-conflicting**: No system services use 9200
- **Memorable**: Easy to remember 92xx pattern for platform
- **Documentation**: Clear service identification

**Port Allocation**:
- Infrastructure: 5432 (PostgreSQL), 6379 (Redis)
- Transcription: 9100
- Platform: 9200
- Future services: 9300+

---

## Framework & Technology Decisions

### Decision: Express.js with TypeScript
**Date**: August 15, 2025  
**Context**: Need robust web framework for API service.

**Decision**: Use Express.js with TypeScript for the platform service.

**Rationale**:
- **Ecosystem**: Mature ecosystem with extensive middleware
- **Team Familiarity**: Common framework choice in Node.js
- **TypeScript**: Strong typing for better code quality
- **Performance**: Proven performance for API services
- **Middleware**: Rich ecosystem (CORS, Helmet, Morgan, etc.)

**Configuration**:
- Strict TypeScript configuration
- Express middleware for security (Helmet), logging (Morgan), CORS
- Structured error handling and validation

**Alternative Considered**: Fastify
- **Rejected**: Express ecosystem more mature for current needs

### Decision: Prisma ORM
**Date**: August 15, 2025  
**Context**: Need type-safe database access layer.

**Decision**: Use Prisma as the ORM for database interactions.

**Rationale**:
- **Type Safety**: Auto-generated TypeScript types
- **Developer Experience**: Excellent tooling and introspection
- **Performance**: Efficient query generation
- **Migrations**: Built-in schema migration system
- **Multi-database**: PostgreSQL support with future flexibility

**Implementation**:
- Prisma Client generated from schema
- Repository pattern for clean architecture
- Connection pooling and optimization built-in

**Alternative Considered**: TypeORM
- **Rejected**: Prisma provides better TypeScript integration

### Decision: Winston for Logging
**Date**: August 15, 2025  
**Context**: Need structured logging for production observability.

**Decision**: Use Winston for application logging.

**Rationale**:
- **Structured Logging**: JSON format for log aggregation
- **Flexibility**: Multiple transport options (file, console, external)
- **Performance**: Asynchronous logging with minimal performance impact
- **Production Ready**: Proven in production environments

**Configuration**:
- JSON format for structured logs
- Different log levels for development vs production
- Service name metadata for log aggregation

---

## Security Architecture Decisions

### Decision: JWT with Redis Sessions
**Date**: August 15, 2025 (Planned for Phase 2)  
**Context**: Need scalable authentication with session management capabilities.

**Decision**: Use JWT tokens for stateless authentication combined with Redis session storage.

**Rationale**:
- **Scalability**: Stateless JWT tokens enable horizontal scaling
- **Performance**: No database lookups for token validation
- **Revocation**: Redis sessions enable token revocation
- **Security**: Short-lived access tokens with refresh tokens
- **Multi-service**: Tokens can be validated by multiple services

**Implementation Plan**:
- Short-lived access tokens (1 hour)
- Longer-lived refresh tokens (7 days)
- Redis session store for token revocation
- Tenant and user context embedded in JWT

### Decision: bcrypt for Password Hashing
**Date**: August 15, 2025 (Planned for Phase 2)  
**Context**: Need secure password storage.

**Decision**: Use bcrypt with cost factor 12 for password hashing.

**Rationale**:
- **Security**: Proven cryptographic algorithm
- **Adaptive**: Cost factor can be increased over time
- **Performance**: Cost factor 12 balances security and performance
- **Industry Standard**: Widely adopted and vetted

---

## Testing Strategy Decisions

### Decision: Jest + Supertest Testing Stack
**Date**: August 15, 2025  
**Context**: Need comprehensive testing framework.

**Decision**: Use Jest for unit testing and Supertest for integration testing.

**Rationale**:
- **Ecosystem**: Mature testing ecosystem for Node.js
- **TypeScript**: Excellent TypeScript support with ts-jest
- **API Testing**: Supertest simplifies HTTP endpoint testing
- **Mocking**: Built-in mocking capabilities for unit tests
- **Coverage**: Integrated code coverage reporting

**Implementation**:
- Unit tests for repositories and utilities
- Integration tests for API endpoints
- Test database setup with cleanup
- Coverage reporting and CI integration

### Decision: KISS Testing Philosophy
**Date**: August 15, 2025  
**Context**: Balance test coverage with development velocity.

**Decision**: Focus on happy path testing with basic error scenarios.

**Rationale**:
- **Velocity**: Get core functionality working quickly
- **Coverage**: Ensure all major features have basic tests
- **Maintainability**: Simple tests are easier to maintain
- **Evolution**: Test suite can grow as features mature

**Test Priorities**:
1.  Core functionality (happy paths)
2.  Database connectivity and operations
3.  API endpoint responses
4. =. Error handling (Phase 2)
5. =. Edge cases (Future phases)

---

## Integration Pattern Decisions

### Decision: Makefile for Service Orchestration
**Date**: August 15, 2025  
**Context**: Need consistent commands for service management.

**Decision**: Extend existing Makefile with platform service commands.

**Rationale**:
- **Consistency**: Follows established Tahoe patterns
- **Simplicity**: Simple commands for common operations
- **Documentation**: Self-documenting service operations
- **Automation**: Easy integration with CI/CD pipelines

**Commands Added**:
- `make platform-up` - Start platform service
- `make platform-down` - Stop platform service  
- `make platform-logs` - View service logs
- `make platform-status` - Check service health
- Updated `make all-up` and `make test` to include platform

---

## Decision Tracking Process

### Decision Documentation
- **Format**: Each decision includes date, context, rationale, alternatives
- **Status**: Track implementation status and any changes
- **Review**: Regular review of decisions for continued relevance
- **Evolution**: Update decisions as requirements change

### Decision Categories
1. **Architecture**: High-level system design decisions
2. **Technology**: Framework and library choices
3. **Security**: Security architecture and implementation
4. **Operations**: Deployment and infrastructure decisions
5. **Process**: Development workflow and methodology decisions