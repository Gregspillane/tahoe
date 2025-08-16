# Tahoe Platform Service Masterplan

## Executive Summary

This document outlines the architecture and implementation plan for the Tahoe Platform Service, which will provide core authentication, authorization, and multi-tenant management for the Tahoe SaaS product. The platform service will integrate with existing infrastructure (PostgreSQL and Redis) and work alongside other microservices including transcription, agent-engine, and loading services.

## Technology Stack

### Primary Language: TypeScript / Node.js

All non-AI services in Tahoe are built with **TypeScript and Node.js**. This includes:
- Platform Service (this service)
- Billing Service (future)
- Notification Service (future)
- Other business logic services

### Core Technologies (Aligned with Tahoe)
- **Language**: TypeScript / Node.js
- **Framework**: Express.js with TypeScript
- **Database**: PostgreSQL (shared `tahoe` database)
- **ORM**: Prisma
- **Cache**: Redis (shared instance)
- **Container**: Docker with Docker Compose
- **Network**: tahoe-network (shared)

### Platform Service Specifics
- **Port**: 9200 (following Tahoe's port pattern)
- **Authentication**: jsonwebtoken + bcryptjs ✅
- **Authorization**: Permission-based access control ✅
- **API Keys**: Secure generation with bcrypt hashing ✅
- **Rate Limiting**: Redis-backed multi-strategy limiting ✅
- **Testing**: Jest + Supertest ✅
- **Logging**: Winston (structured logging) ✅

### Redis Namespacing
Platform service will use prefixed keys:
- `platform:session:*` - User sessions
- `platform:rate_limit:*` - Rate limiting
- `platform:cache:*` - General cache
- `platform:events:*` - Event queue

## Architecture Overview

### Core Principles
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering
- **Secure by Default**: Row-level tenant isolation, encrypted communications
- **Flexible**: Room for evolution without major rewrites
- **Microservices-Ready**: Designed to work with Tahoe's distributed architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Gateway   │ ← External requests (HTTPS)
└────────┬────────┘
         │ JWT validation
         ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│Platform Service │────►│ Transcribe   │────►│Agent Engine │────►│   Loading   │
│  (Core Auth)    │     │   Service    │     │   Service   │     │   Service   │
└────────┬────────┘     └──────┬───────┘     └──────┬──────┘     └──────┬──────┘
         │                     │                     │                     │
         ▼                     ▼                     ▼                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure (tahoe-network)                      │
│  ┌────────────────────────────┐        ┌─────────────────────────────────┐  │
│  │   PostgreSQL (tahoe DB)     │        │   Redis (Cache & Queue)        │  │
│  │   - platform schema         │        │   - session:*                  │  │
│  │   - transcription tables    │        │   - transcription:*            │  │
│  │   - agent_engine tables     │        │   - platform:*                 │  │
│  └────────────────────────────┘        └─────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ Billing Service │     │Audit Service │     │Notification │
│    (Future)     │     │   (Future)   │     │   Service   │
└─────────────────┘     └──────────────┘     └─────────────┘
```

### Service Integration Points

**Platform Service** will be deployed as:
```
tahoe/
├── infrastructure/      # ✓ Already exists (PostgreSQL + Redis)
├── transcribe/         # ✓ Already exists 
├── agent-engine/       # In development
├── loading/           # Planned
├── platform/          # NEW - Core auth & tenant management
├── billing/           # Future service
└── notifications/     # Future service
```

## Data Models

### Prisma Schema Design

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

enum TenantStatus {
  ACTIVE
  SUSPENDED
  TRIAL
  INACTIVE
}

enum UserStatus {
  ACTIVE
  INVITED
  SUSPENDED
  INACTIVE
}

enum UserRole {
  ADMIN
  MANAGER
  USER
}

model Tenant {
  id        String       @id @default(uuid())
  name      String       @db.VarChar(255)
  slug      String       @unique @db.VarChar(100)
  status    TenantStatus @default(TRIAL)
  planTier  String       @default("free") @map("plan_tier") @db.VarChar(50)
  settings  Json         @default("{}")
  createdAt DateTime     @default(now()) @map("created_at")
  updatedAt DateTime     @updatedAt @map("updated_at")
  deletedAt DateTime?    @map("deleted_at")

  users        User[]
  apiKeys      ApiKey[]
  sessions     Session[]
  featureFlags FeatureFlag[]
  events       Event[]

  @@index([slug])
  @@index([status])
  @@map("tenants")
}

model User {
  id           String     @id @default(uuid())
  email        String     @unique @db.VarChar(255)
  tenantId     String     @map("tenant_id")
  role         UserRole   @default(USER)
  firstName    String     @map("first_name") @db.VarChar(100)
  lastName     String     @map("last_name") @db.VarChar(100)
  passwordHash String     @map("password_hash") @db.VarChar(255)
  status       UserStatus @default(INVITED)
  lastLoginAt  DateTime?  @map("last_login_at")
  createdAt    DateTime   @default(now()) @map("created_at")
  updatedAt    DateTime   @updatedAt @map("updated_at")
  deletedAt    DateTime?  @map("deleted_at")

  tenant      Tenant    @relation(fields: [tenantId], references: [id])
  sessions    Session[]
  apiKeys     ApiKey[]
  events      Event[]

  @@index([tenantId, email])
  @@index([email])
  @@map("users")
}

model ApiKey {
  id          String    @id @default(uuid())
  tenantId    String    @map("tenant_id")
  name        String    @db.VarChar(100)
  keyHash     String    @map("key_hash") @db.VarChar(255)
  keyPrefix   String    @map("key_prefix") @db.VarChar(10)
  permissions Json      @default("[]")
  lastUsedAt  DateTime? @map("last_used_at")
  expiresAt   DateTime? @map("expires_at")
  createdBy   String    @map("created_by")
  createdAt   DateTime  @default(now()) @map("created_at")
  revokedAt   DateTime? @map("revoked_at")

  tenant Tenant @relation(fields: [tenantId], references: [id])
  user   User   @relation(fields: [createdBy], references: [id])

  @@index([keyPrefix])
  @@index([tenantId])
  @@map("api_keys")
}

model Session {
  id        String   @id @default(uuid())
  userId    String   @map("user_id")
  tenantId  String   @map("tenant_id")
  tokenHash String   @map("token_hash") @db.VarChar(255)
  ipAddress String?  @map("ip_address") @db.Inet
  userAgent String?  @map("user_agent") @db.Text
  expiresAt DateTime @map("expires_at")
  createdAt DateTime @default(now()) @map("created_at")

  user   User   @relation(fields: [userId], references: [id])
  tenant Tenant @relation(fields: [tenantId], references: [id])

  @@index([tokenHash])
  @@index([userId, tenantId])
  @@map("sessions")
}

model FeatureFlag {
  id          String   @id @default(uuid())
  tenantId    String   @map("tenant_id")
  featureName String   @map("feature_name") @db.VarChar(100)
  enabled     Boolean  @default(false)
  config      Json     @default("{}")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  tenant Tenant @relation(fields: [tenantId], references: [id])

  @@unique([tenantId, featureName])
  @@map("feature_flags")
}

model Event {
  id        String   @id @default(uuid())
  tenantId  String?  @map("tenant_id")
  userId    String?  @map("user_id")
  eventType String   @map("event_type") @db.VarChar(100)
  payload   Json
  createdAt DateTime @default(now()) @map("created_at")

  tenant Tenant? @relation(fields: [tenantId], references: [id])
  user   User?   @relation(fields: [userId], references: [id])

  @@index([tenantId, createdAt])
  @@index([eventType, createdAt])
  @@map("events")
}
```

## API Specifications (✅ IMPLEMENTED)

### Authentication Endpoints ✅

#### POST /api/v1/auth/login ✅
```json
Request:
{
  "email": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "admin",
    "tenant": {
      "id": "uuid",
      "name": "Acme Corp",
      "slug": "acme-corp"
    }
  }
}
```

#### POST /api/v1/auth/refresh ✅
```json
Request:
{
  "refresh_token": "eyJ..."
}

Response:
{
  "access_token": "eyJ...",
  "expires_in": 3600
}
```

#### POST /api/v1/auth/validate (Internal Only) ✅
```json
Request Headers:
X-Service-Token: shared_secret_token

Request:
{
  "token": "eyJ..."
}

Response:
{
  "valid": true,
  "tenant_id": "uuid",
  "user_id": "uuid",
  "role": "admin",
  "permissions": ["read", "write", "delete"]
}
```

### API Key Management Endpoints ✅

#### POST /api/v1/api-keys ✅
Create new API key with permission scoping

#### GET /api/v1/api-keys ✅
List API keys for authenticated tenant

#### GET /api/v1/api-keys/{id} ✅
Get API key details (masked key)

#### PATCH /api/v1/api-keys/{id} ✅
Update API key name, permissions, or expiration

#### DELETE /api/v1/api-keys/{id} ✅
Revoke API key

### Tenant Management Endpoints (Phase 4)

#### GET /api/v1/tenants/{id} (Future)
#### PATCH /api/v1/tenants/{id} (Future)
#### GET /api/v1/tenants/{id}/features (Future)
#### POST /api/v1/tenants/{id}/features (Future)

### User Management Endpoints (Phase 4)

#### GET /api/v1/tenants/{tenant_id}/users (Future)
#### POST /api/v1/tenants/{tenant_id}/users (Future)
#### PATCH /api/v1/tenants/{tenant_id}/users/{id} (Future)
#### DELETE /api/v1/tenants/{tenant_id}/users/{id} (Future)
#### POST /api/v1/tenants/{tenant_id}/users/{id}/invite (Future)
#### POST /api/v1/tenants/{tenant_id}/users/{id}/reset-password (Future)

## Service Communication

### Internal Service Authentication

Tahoe services communicate internally using the tahoe-network. The platform service provides authentication for all services:

1. **External requests** → Platform Service validates JWT → Returns tenant/user context
2. **Service-to-service** → Uses SERVICE_TOKEN + tenant context headers
3. **Transcribe Service** → Validates requests through Platform Service
4. **Agent Engine** → Inherits tenant context from upstream services
5. **Loading Service** → Associates uploaded files with tenants

### Integration with Existing Services

**Transcription Service Integration:**
- All transcription jobs tagged with tenant_id
- Platform service validates API keys before job submission
- Usage tracking for transcription minutes per tenant

**Agent Engine Integration:**
- Agent analysis scoped to tenant
- Platform service provides user permissions for agent access
- Audit trail for all agent operations

**Loading Service Integration:**
- File uploads associated with tenant storage quotas
- Platform service enforces file size/count limits
- Multi-tenant file isolation

### API Gateway Pattern

Platform service acts as the authentication gateway:
```
External Request → Platform Service (Auth) → Target Service
                         ↓
                  Adds Headers:
                  - X-Tenant-ID
                  - X-User-ID  
                  - X-Permissions
```

## Security Implementation

### Tenant Isolation
- Every table includes `tenant_id` column
- All queries automatically filtered by tenant_id
- Repository pattern enforces tenant context
- Database-level RLS (Row Level Security) as additional safeguard

### Password Security
- Bcrypt with cost factor 12
- Minimum 8 characters, complexity requirements
- Password reset tokens expire in 1 hour
- Account lockout after 5 failed attempts

### API Security
- Rate limiting: 100 requests/minute per tenant
- API keys scoped to specific permissions
- All external traffic over HTTPS
- CORS configured for specific origins

### Audit Requirements
Critical events to audit:
- User login/logout
- Permission changes
- Tenant configuration changes
- API key creation/revocation
- Failed authentication attempts

## Implementation Phases

### Development Approach with Claude Code ✅
- **100% Claude Code Development** - All coding completed using Claude Code ✅
- **Session-based work** - Each session completed full units of work ✅
- **Context management** - Logical chunks completed with proper handoff ✅
- **Memory bank system** - Complete documentation and decision tracking ✅

### ✅ COMPLETED: Phase 1: Core Foundation (1 Session)

**✅ Session 1: Service Setup & Database (August 15, 2025)**
- [x] Create platform service directory structure
- [x] Set up Docker configuration following Tahoe patterns
- [x] Configure Prisma with shared database connection
- [x] Design schema to coexist with transcription tables
- [x] Implement base models (Tenant, User, ApiKey, Session, FeatureFlag, Event)
- [x] **Write tests**: Database connection, basic model creation
- [x] Complete and verify service starts correctly
- [x] Makefile integration for platform service commands

### ✅ COMPLETED: Phase 2: Authentication & Authorization (2 Sessions)

**✅ Session 2.1: Authentication System (August 15, 2025)**
- [x] JWT token generation/validation with permissions
- [x] Login/logout endpoints with tenant context
- [x] **Write tests**: Successful login returns token with permissions
- [x] Password hashing with bcryptjs (cost factor 12)
- [x] Session management in Redis with revocation
- [x] **Write tests**: Session stores and retrieves correctly
- [x] Refresh token flow
- [x] **Write tests**: Refresh token returns new access token
- [x] Internal service token validation
- [x] Verify full auth flow works end-to-end

**✅ Session 2.2: Authorization & API Keys (August 16, 2025)**
- [x] Advanced permission-based authorization system
- [x] **Write tests**: Permission validation works correctly
- [x] API key generation and management with CRUD endpoints
- [x] **Write tests**: API key authenticates successfully
- [x] Enhanced tenant context middleware with deep validation
- [x] Rate limiting with Redis (multiple strategies)
- [x] **Write tests**: Rate limiting enforces limits correctly
- [x] Service authentication with registry and heartbeat
- [x] Usage tracking and analytics foundations
- [x] Comprehensive test suite for all authorization features

### 🟡 CURRENT: Phase 3: Service Integration (2 Sessions)

**⏳ Session 3.1: Transcription Service Integration (Next)**
- [ ] Update transcription service to use platform auth
- [ ] **Write test**: Transcription service accepts platform tokens
- [ ] Add tenant_id to transcription jobs and data
- [ ] Implement usage tracking for transcriptions
- [ ] **Write test**: Usage increments correctly for transcription events
- [ ] Cross-service communication patterns
- [ ] Verify transcription service fully integrated

**⏳ Session 3.2: Event System & Analytics**
- [ ] Event publishing system for audit logging
- [ ] **Write test**: Events publish and consume successfully
- [ ] Real-time usage analytics dashboard
- [ ] Feature flag system enhancement
- [ ] **Write test**: Feature flags enable/disable correctly
- [ ] Comprehensive audit logging
- [ ] Cross-service event correlation

### 🔲 FUTURE: Phase 4: Operational Features (3 Sessions)

**Session 4.1: User Management**
- [ ] User invitation flow
- [ ] **Write test**: Invitation creates pending user
- [ ] Email verification (stub for now)
- [ ] Password reset flow
- [ ] **Write test**: Password reset token works
- [ ] User profile management
- [ ] Tenant admin capabilities

**Session 4.2: Platform APIs**
- [ ] Tenant onboarding flow
- [ ] **Write test**: New tenant setup completes
- [ ] Usage analytics endpoints
- [ ] Admin dashboard APIs
- [ ] Service status aggregation
- [ ] **Write test**: Status endpoint returns all services
- [ ] Metrics collection enhancement

**Session 4.3: Production Readiness**
- [ ] Integration tests with all services
- [ ] **Write test**: Full multi-service auth flow works end-to-end
- [ ] Performance testing (basic load test)
- [ ] Production monitoring and alerting
- [ ] Documentation completion
- [ ] Final verification of all components

### Claude Code Session Guidelines

**Starting a Session:**
1. Load the masterplan and relevant context
2. Focus on completing the entire session's tasks
3. Write tests immediately after each feature
4. Commit working code before ending session

**Session Handoff:**
- Each session should end with working, tested code
- Document any decisions or changes made
- Note any blockers or dependencies for next session
- Ensure service runs and passes all tests

**Parallel Sessions:**
- While one Claude Code works on Platform Service Session 2
- Another can work on Billing Service Session 1
- Services integrate through well-defined APIs

## Testing Philosophy - KISS

### Write Tests As You Code
- **Every feature gets a happy path test** - Write the test immediately after the feature
- **Focus on what works** - Test successful scenarios, not edge cases
- **Keep tests simple** - If a test is complex, the code is probably too complex
- **No test debt** - Don't move on without basic test coverage

### Testing Approach

```typescript
// Example: Simple happy path test
describe('POST /api/v1/auth/login', () => {
  it('should login user successfully', async () => {
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({ email: 'test@test.com', password: 'password' });
    
    expect(response.status).toBe(200);
    expect(response.body.access_token).toBeDefined();
  });
});
```

### What to Test
- ✅ Successful API responses
- ✅ Basic database operations work
- ✅ Tokens are generated correctly
- ✅ Services integrate properly

### What NOT to Test (for now)
- ❌ Every possible error condition
- ❌ Complex edge cases
- ❌ Performance limits
- ❌ Malformed input variations

### Test Coverage Goals
- **Aim for breadth, not depth** - Every endpoint has at least one test
- **Integration over unit** - Test that features work end-to-end
- **No blocking on coverage %** - Some tests are better than no tests

## Configuration Management

### Environment Variables Structure

Following Tahoe's pattern, the platform service will have:

```env
# platform/.env

# Service Configuration
NODE_ENV=development
PORT=9200
SERVICE_NAME=platform

# Database (uses shared infrastructure)
DATABASE_URL=postgresql://tahoe_user:tahoe_pass@tahoe-postgres:5432/tahoe

# Redis (uses shared infrastructure)
REDIS_URL=redis://tahoe-redis:6379

# Security
JWT_SECRET=your-256-bit-secret
JWT_EXPIRY=3600
REFRESH_TOKEN_EXPIRY=604800
SERVICE_TOKEN=internal-service-secret
BCRYPT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Feature Flags
DEFAULT_TRIAL_DAYS=14
MAX_USERS_PER_TENANT=100
```

### Docker Compose Integration

The platform service will follow Tahoe's Docker patterns:

```yaml
# platform/docker-compose.yml
version: '3.8'

services:
  platform:
    build: .
    container_name: tahoe-platform
    ports:
      - "9200:9200"
    networks:
      - tahoe-network
    env_file:
      - .env
    depends_on:
      - infrastructure
    volumes:
      - ./src:/app/src
    restart: unless-stopped

networks:
  tahoe-network:
    external: true
```

## Makefile Integration

Following Tahoe's pattern, add these commands to the main Makefile:

```makefile
# Platform Service Commands
platform-up:
	cd platform && docker-compose up -d

platform-down:
	cd platform && docker-compose down

platform-logs:
	cd platform && docker-compose logs -f

platform-restart:
	cd platform && docker-compose restart

platform-status:
	@echo "Platform Service Status:"
	@curl -s http://localhost:9200/health || echo "Platform service not responding"

# Updated all-up command
all-up: infra-up transcribe-up platform-up
	@echo "All services started"

# Updated all-down command  
all-down: transcribe-down platform-down infra-down
	@echo "All services stopped"
```

## Development Workflow

### Local Development Setup

1. **Start infrastructure** (PostgreSQL + Redis):
   ```bash
   make infra-up
   ```

2. **Run Prisma migrations** for platform service:
   ```bash
   cd platform
   npx prisma migrate dev
   ```

3. **Start platform service**:
   ```bash
   make platform-up
   ```

4. **Start other services** that depend on auth:
   ```bash
   make transcribe-up
   ```

### Testing Service Integration

```bash
# Test platform health
curl http://localhost:9200/health

# Create test tenant and user
curl -X POST http://localhost:9200/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Company", "slug": "test-co"}'

# Test authentication flow
curl -X POST http://localhost:9200/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "password"}'

# Verify transcription service uses auth
curl http://localhost:9100/test/submit-job \
  -H "Authorization: Bearer {token}"
```

## Appendix

### Sample Repository Pattern (TypeScript with Prisma)

```typescript
// prisma/schema.prisma excerpt
model Tenant {
  id        String   @id @default(uuid())
  name      String
  slug      String   @unique
  status    TenantStatus
  planTier  String   @map("plan_tier")
  settings  Json
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  deletedAt DateTime? @map("deleted_at")
  
  users     User[]
  apiKeys   ApiKey[]
  sessions  Session[]
  features  FeatureFlag[]
  
  @@map("tenants")
}

// src/repositories/tenant.repository.ts
import { PrismaClient } from '@prisma/client';

export class TenantRepository {
  constructor(private prisma: PrismaClient) {}
  
  async findById(tenantId: string, includeDeleted = false) {
    return this.prisma.tenant.findFirst({
      where: {
        id: tenantId,
        ...(!includeDeleted && { deletedAt: null })
      }
    });
  }
  
  async findUsers(tenantId: string) {
    return this.prisma.user.findMany({
      where: {
        tenantId,
        deletedAt: null
      },
      orderBy: { createdAt: 'desc' }
    });
  }
}
```

### Sample Middleware (TypeScript with Express)

```typescript
// src/middleware/tenant-context.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { verifyJWT } from '../utils/jwt';
import { PrismaClient } from '@prisma/client';

interface AuthRequest extends Request {
  tenantId?: string;
  userId?: string;
  role?: string;
  prisma?: PrismaClient;
}

export const requireTenantContext = async (
  req: AuthRequest, 
  res: Response, 
  next: NextFunction
) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const claims = await verifyJWT(token);
    
    req.tenantId = claims.tenant;
    req.userId = claims.sub;
    req.role = claims.role;
    
    // Extend Prisma with automatic tenant filtering
    req.prisma = prismaWithTenant(req.tenantId);
    
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Prisma extension for automatic tenant filtering
function prismaWithTenant(tenantId: string) {
  return prisma.$extends({
    query: {
      $allModels: {
        async $allOperations({ args, query }) {
          if (args.where) {
            args.where = { ...args.where, tenantId };
          }
          return query(args);
        }
      }
    }
  });
}
```

---

## Document Version
- Version: 2.0
- Last Updated: August 16, 2025
- Status: ✅ Phase 1 & 2 Complete - Service Integration Ready

## ✅ Completed Milestones
1. ✅ Architecture approved and implemented
2. ✅ Technology stack selected and operational
3. ✅ Development environment fully functional
4. ✅ Phase 1: Core Foundation completed (1 session)
5. ✅ Phase 2: Authentication & Authorization completed (2 sessions)

## 🎯 Next Steps (Phase 3)
1. **Session 3.1**: Integrate transcription service with platform auth
2. **Session 3.2**: Implement event system and real-time analytics
3. Continue with service integration across Tahoe ecosystem
4. Build operational features and production readiness

## 📊 Current Status
- **Platform Service**: ✅ Fully operational on port 9200
- **Authentication**: ✅ JWT + API key systems complete
- **Authorization**: ✅ Permission-based access control operational
- **Rate Limiting**: ✅ Multi-strategy Redis-backed limiting active
- **Usage Tracking**: ✅ Foundation implemented and logging events
- **Testing**: ✅ Comprehensive test suite with 100% critical path coverage
- **Service Health**: ✅ http://localhost:9200/health responding correctly