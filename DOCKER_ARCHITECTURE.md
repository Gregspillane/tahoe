# Tahoe Platform - Docker Architecture

## Overview

The Tahoe platform uses a **distributed service architecture** where each service runs independently, connected through a shared Docker network.

## Architecture Principles

### ✅ **Fixed**: Independent Service Containers
- Each service (agent-engine, auth, billing) runs in its own container
- Services are **not nested** within the main tahoe project container
- Infrastructure services (PostgreSQL, Redis) are shared across all services

### 🏗️ **Infrastructure Layer**
- **PostgreSQL**: Shared database with schema isolation
- **Redis**: Shared cache with namespace isolation  
- **Network**: Common `tahoe-network` for inter-service communication

### 🚀 **Service Layer**
- **agent-engine**: AI orchestration service (port 8001)
- **auth**: Authentication service (port 8002, future)
- **billing**: Billing service (port 8003, future)

## Container Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Host                            │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ tahoe-postgres  │  │  tahoe-redis    │  │ tahoe-agent  │ │
│  │ (port 5432)     │  │  (port 6379)    │  │ -engine      │ │
│  │                 │  │                 │  │ (port 8001)  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                   │       │
│           └─────────────────────┼───────────────────┘       │
│                                 │                           │
│                        tahoe-network                       │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ tahoe-auth      │  │ tahoe-billing   │                  │
│  │ (port 8002)     │  │ (port 8003)     │                  │
│  │ [future]        │  │ [future]        │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Service Startup Sequence

### 1. Start Infrastructure
```bash
# Start PostgreSQL and Redis
make up
# OR
docker-compose up -d
```

### 2. Start Individual Services
```bash
# Start agent-engine
cd services/agent-engine
make docker-up

# Future services
cd services/auth && make up
cd services/billing && make up  
```

## Service Configuration

### Infrastructure Services
- **Location**: Root `docker-compose.yml`
- **Network**: Creates `tahoe-network`
- **Storage**: Persistent volumes for data

### Agent Engine Service  
- **Location**: `services/agent-engine/docker-compose.yml`
- **Network**: Connects to external `tahoe-network`
- **Configuration**: Uses root `.env` file
- **Dependencies**: Requires infrastructure services

## Environment Variables

### Infrastructure (.env at root)
```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=tahoe
DATABASE_USER=tahoe_user
DATABASE_PASSWORD=changeme

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Service-specific
AGENT_ENGINE_PORT=8001
AGENT_ENGINE_DB_SCHEMA=agent_engine
AGENT_ENGINE_REDIS_NAMESPACE=agent:
```

### Service Discovery
Services discover each other via:
- **Development**: localhost with different ports
- **Docker**: service names within tahoe-network
- **Production**: Environment-specific URLs

## Development Workflows

### Full Platform Development
```bash
# 1. Start infrastructure
make up

# 2. Start services  
cd services/agent-engine && make docker-up

# 3. View all services
docker ps
```

### Service-Specific Development
```bash
# Infrastructure only
make up

# Agent-engine development (without Docker)
cd services/agent-engine && make dev
```

### Testing and Validation
```bash
# Validate R1 Foundation
python scripts/validate_r1_foundation.py

# Test agent-engine specifically
cd services/agent-engine && make validate
```

## Service Isolation

### Database Isolation
- Each service uses PostgreSQL schemas
- Connection strings: `postgresql://user:pass@host:port/db?schema=service_name`
- Examples:
  - agent-engine: `?schema=agent_engine`
  - auth: `?schema=auth_service`
  - billing: `?schema=billing_service`

### Redis Isolation
- Each service uses Redis namespaces
- Key patterns: `service:namespace:key`
- Examples:
  - agent-engine: `agent:session:123`
  - auth: `auth:token:456`  
  - billing: `billing:invoice:789`

### Network Isolation
- All services share `tahoe-network`
- Internal communication via service names
- External access via mapped ports

## Benefits of This Architecture

### ✅ **Independent Deployment**
- Each service can be deployed separately
- No nested containers or dependencies
- Clear service boundaries

### ✅ **Development Flexibility**
- Run infrastructure once, develop services individually
- Hot reload for active development
- Easy to test individual components

### ✅ **Production Scalability**
- Horizontal scaling per service
- Independent resource allocation
- Service-specific configurations

### ✅ **Operational Clarity**
- Clear container hierarchy in Docker Desktop
- Easy to monitor and debug individual services
- Separate logs and metrics per service

## Migration Notes

### Fixed Issues
- ❌ **Before**: agent-engine was nested within tahoe project container
- ✅ **After**: agent-engine runs as independent service container

### Architecture Changes
1. Moved agent-engine to its own `docker-compose.yml`
2. Updated root `docker-compose.yml` to infrastructure-only
3. Created named network for service discovery
4. Updated Makefiles for independent service management

This architecture now properly reflects a microservices pattern with independent, scalable services.