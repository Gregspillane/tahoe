# Tahoe Database Architecture

## Overview

The Tahoe platform uses a **shared database with bounded contexts** approach, providing a balance between microservices independence and operational simplicity. This document outlines the architectural principles, design patterns, and implementation guidelines for database interactions across all Tahoe services.

See [infrastructure/README.md](README.md) for infrastructure setup and connection details.

## Architecture Decision

**Decision**: Continue with shared PostgreSQL database (`tahoe`) with clear domain boundaries and ownership patterns.

**Date**: August 16, 2025

**Context**: Multi-service platform requiring strong data consistency for authentication, authorization, and billing while maintaining service independence for domain-specific operations.

## Core Principles

### 1. Shared Core Database with Domain Boundaries

```
┌─────────────────────────────────────────┐
│          Shared Core Database           │
│  (PostgreSQL - tahoe)                   │
├─────────────────────────────────────────┤
│  Core Domain (Platform Service Owns)    │
│  - tenants                              │
│  - users                                │
│  - api_keys                             │
│  - sessions                             │
│  - feature_flags                        │
│  - events (audit logging)               │
└─────────────────────────────────────────┘
           ↑ Read-only access ↑
┌─────────────────────────────────────────┐
│    Service-Specific Tables/Schemas      │
├─────────────────────────────────────────┤
│  Transcription Domain                   │
│  - transcription_jobs (with tenant_id)  │
│  - transcription_chunks                 │
│  - transcription_results                │
├─────────────────────────────────────────┤
│  Analytics Domain (Future)              │
│  - usage_metrics (with tenant_id)       │
│  - analytics_events                     │
├─────────────────────────────────────────┤
│  Billing Domain (Future)                │
│  - invoices (with tenant_id)            │
│  - payment_methods                      │
└─────────────────────────────────────────┘
```

### 2. Domain Ownership Rules

**Platform Service (Core Domain Owner)**:
- **OWNS**: `tenants`, `users`, `api_keys`, `sessions`, `feature_flags`, `events`
- **RESPONSIBILITIES**: Authentication, authorization, user management, tenant management
- **ACCESS PATTERN**: Full read/write access to core tables
- **EVENT PUBLISHING**: Publishes changes to core entities for other services

**Other Services (Domain-Specific Owners)**:
- **OWNS**: Service-specific tables (e.g., `transcription_jobs`, `analytics_metrics`)
- **RESPONSIBILITIES**: Domain-specific business logic and data management
- **ACCESS PATTERN**: Read-only access to core tables, full access to owned tables
- **TENANT ISOLATION**: All owned tables must include `tenant_id` foreign key

### 3. Data Access Patterns

#### Repository Pattern Implementation

```typescript
// Platform Service - Core Domain Owner
export class UserRepository {
  constructor(private db: PrismaClient) {}

  async updateUser(id: string, data: UpdateUserData) {
    const user = await this.db.user.update({
      where: { id },
      data
    });
    
    // Platform service publishes events for core entity changes
    await EventBus.publish('user.updated', {
      userId: id,
      tenantId: user.tenantId,
      changes: data,
      timestamp: new Date()
    });
    
    return user;
  }
}

// Transcription Service - Domain-Specific Owner
export class TranscriptionJobRepository {
  constructor(private db: PrismaClient) {}

  async createJob(data: CreateJobData) {
    // Validate against core tables (read-only)
    const user = await this.db.user.findFirst({
      where: { 
        id: data.userId, 
        tenantId: data.tenantId,
        status: 'ACTIVE'
      }
    });
    
    if (!user) {
      throw new Error('Invalid user or tenant');
    }
    
    // Create in service-specific table
    return await this.db.transcriptionJob.create({
      data: {
        ...data,
        tenantId: data.tenantId // Ensure tenant isolation
      }
    });
  }
}
```

### 4. Tenant Isolation Strategy

**Mandatory Tenant Isolation**:
- All service-specific tables MUST include `tenant_id` column
- All queries MUST filter by `tenant_id` at the repository level
- Database indexes MUST include `tenant_id` for performance

**Implementation Pattern**:
```typescript
// Correct: Tenant-scoped query
async findTranscriptionsByTenant(tenantId: string) {
  return await this.db.transcriptionJob.findMany({
    where: { tenantId } // Required for all queries
  });
}

// Incorrect: Global query without tenant isolation
async findAllTranscriptions() {
  return await this.db.transcriptionJob.findMany({}); // ❌ Never do this
}
```

## Database Schema Guidelines

### Core Tables (Platform Service Owned)

```sql
-- Core domain tables owned by Platform Service
CREATE TABLE tenants (
  id UUID PRIMARY KEY,
  name VARCHAR NOT NULL,
  status VARCHAR NOT NULL, -- ACTIVE, TRIAL, SUSPENDED
  plan_tier VARCHAR NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id),
  email VARCHAR UNIQUE NOT NULL,
  role VARCHAR NOT NULL, -- ADMIN, MANAGER, USER
  status VARCHAR NOT NULL, -- ACTIVE, SUSPENDED
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

### Service-Specific Tables

```sql
-- Service-specific tables owned by individual services
CREATE TABLE transcription_jobs (
  id UUID PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id), -- Required for isolation
  user_id UUID REFERENCES users(id),
  status VARCHAR NOT NULL,
  audio_url VARCHAR,
  transcript_text TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes including tenant_id for performance
CREATE INDEX idx_transcription_jobs_tenant_id ON transcription_jobs(tenant_id);
CREATE INDEX idx_transcription_jobs_user_id ON transcription_jobs(user_id);
CREATE INDEX idx_transcription_jobs_status_tenant ON transcription_jobs(status, tenant_id);
```

## Implementation Guidelines

### 1. Repository Pattern Rules

**All repositories MUST**:
- Accept database instance via dependency injection
- Implement tenant-scoped queries by default
- Include proper error handling for tenant validation
- Use TypeScript types for all operations

**Example Implementation**:
```typescript
export class BaseRepository {
  constructor(protected db: PrismaClient) {}
  
  protected ensureTenantScope(query: any, tenantId: string) {
    return {
      ...query,
      where: {
        ...query.where,
        tenantId
      }
    };
  }
}

export class TranscriptionRepository extends BaseRepository {
  async findByTenant(tenantId: string) {
    return await this.db.transcriptionJob.findMany(
      this.ensureTenantScope({}, tenantId)
    );
  }
}
```

### 2. Event Broadcasting Pattern

**Core entity changes MUST be broadcasted**:
```typescript
interface DomainEvent {
  type: string;
  tenantId: string;
  entityId: string;
  payload: any;
  timestamp: Date;
}

// Platform service publishes events
await EventBus.publish('tenant.created', {
  type: 'tenant.created',
  tenantId: tenant.id,
  entityId: tenant.id,
  payload: { name: tenant.name, plan: tenant.planTier },
  timestamp: new Date()
});

// Other services can subscribe to events
EventBus.subscribe('tenant.updated', async (event: DomainEvent) => {
  // Handle tenant updates in service-specific logic
  await this.handleTenantUpdate(event);
});
```

### 3. Database Permissions (Future Enhancement)

**Read-Only Access for Core Tables**:
```sql
-- Create read-only role for non-platform services
CREATE ROLE transcription_service;

-- Grant read access to core tables
GRANT SELECT ON tenants, users, api_keys TO transcription_service;

-- Grant full access to service-specific tables
GRANT ALL ON transcription_jobs, transcription_chunks TO transcription_service;
```

## Benefits of This Approach

### Advantages
1. **Strong Consistency**: ACID transactions across related entities
2. **Simplified Queries**: Direct JOINs between tenant/user/service data
3. **Single Source of Truth**: No data synchronization complexity
4. **Operational Simplicity**: One database to backup, monitor, and scale
5. **Cost Effective**: Single database instance
6. **Development Velocity**: Faster feature development with direct data access

### Trade-offs Accepted
1. **Schema Coordination**: Core table changes require cross-service coordination
2. **Shared Scaling**: All services share database resources
3. **Single Point of Failure**: Database outage affects all services

## Migration Strategy

### Phase 1: Current State (Implemented)
- Shared database with table separation
- Repository pattern for data access
- Tenant isolation via `tenant_id` columns

### Phase 2: Enhanced Boundaries (Next)
- Database views for read-only access to core tables
- Event broadcasting for core entity changes
- Database user permissions for access control

### Phase 3: Event Sourcing (Future)
- Event store for audit logging
- Eventual consistency patterns where appropriate
- Prepare for potential database separation

### Phase 4: Database Separation (If Needed)
- Move to database-per-service if requirements change
- Event sourcing for cross-service communication
- Service mesh for complex data relationships

## Decision Framework

**When to Consider Database Separation**:
- Dedicated teams per service with independent deployment cycles
- Services have vastly different scaling patterns
- Need for different database technologies (e.g., time-series, graph)
- Service domains become truly independent

**When to Keep Shared Database**:
- Small team with shared responsibility
- Strong data relationships between services
- Need for strong consistency (billing, permissions)
- Operational simplicity is important

## Conclusion

The shared database with bounded contexts approach is optimal for Tahoe's current stage and requirements. It provides:

- **Immediate Development Velocity**: Fast feature development without complex data synchronization
- **Strong Consistency**: Critical for B2B SaaS billing and permissions
- **Clear Evolution Path**: Can migrate to full service separation when needed
- **Operational Simplicity**: Manageable complexity for small teams

This architecture should be maintained until clear requirements emerge for service independence that outweigh the benefits of the shared approach.