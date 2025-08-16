# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Building and Testing
```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run tests
npm test

# Run tests in watch mode
npm test:watch

# Run tests with coverage
npm test:coverage

# Run linting
npm run lint

# Auto-fix linting issues
npm run lint:fix
```

### Database Operations
```bash
# Generate Prisma client
npm run prisma:generate

# Run database migrations (development)
npm run prisma:migrate

# Deploy migrations (production)
npm run prisma:deploy

# Open Prisma Studio
npm run prisma:studio
```

### Service Operations (via Makefile)
```bash
# Start infrastructure (PostgreSQL + Redis) first
make infra-up

# Start platform service
make platform-up

# Check service status
make platform-status

# View logs
make platform-logs

# Stop services
make platform-down

# Start all services
make all-up
```

## Architecture Overview

### Multi-tenant SaaS Platform Service
The Tahoe Platform Service provides core authentication, authorization, and multi-tenant management. It runs on port 9200 and integrates with shared PostgreSQL and Redis infrastructure.

**Technology Stack:**
- TypeScript/Node.js with Express.js
- Prisma ORM with PostgreSQL (shared `tahoe` database)
- Redis for sessions and caching
- Docker with shared tahoe-network
- JWT authentication with bcrypt password hashing

### Service Integration Pattern
- **Platform Service** (port 9200): Core auth and tenant management
- **Transcription Service** (port 9100): Uses platform auth
- **Shared Infrastructure**: PostgreSQL + Redis on tahoe-network

### Database Schema Design
All models include tenant isolation with `tenantId` fields. Core models:
- **Tenant**: Organization accounts with status, plan tier, settings
- **User**: Individual users within tenants with roles (ADMIN/MANAGER/USER)
- **ApiKey**: Service access keys with permissions
- **Session**: User sessions in database + Redis
- **FeatureFlag**: Per-tenant feature toggles
- **Event**: Audit and analytics events

### Repository Pattern with Tenant Context
The codebase uses repository pattern with automatic tenant filtering. When adding new features:
1. Extend Prisma models with proper tenant relationships
2. Use tenant-scoped repositories for data access
3. Add appropriate database indexes for performance
4. Include tenant context in all middleware

### Testing Philosophy
- Write happy path tests immediately after each feature
- Focus on integration tests over unit tests
- Test database operations and API endpoints
- Use Jest with Supertest for API testing
- Simple test setup in `tests/setup.ts`

### Security Requirements
- All database queries automatically filtered by tenant_id
- JWT tokens include tenant context
- API keys scoped to specific permissions
- Rate limiting per tenant
- Audit logging for critical events

### Common Development Patterns
- All API routes require tenant context middleware
- Database operations use tenant-scoped Prisma client
- Error handling with structured logging via Winston
- Environment configuration through .env files
- Docker health checks for service monitoring

### Phase-based Development
Currently in Phase 1 (Core Foundation). Future phases include:
- Phase 2: Service Integration with existing Tahoe services
- Phase 3: Advanced features (user management, analytics)

When adding new features, follow the established patterns for tenant isolation, testing, and Docker integration.
- we are running within docker containers running locally on docker desktop. Don't try to build or install locally with simple NPM commands