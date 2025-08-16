# Tahoe Platform Service

The Platform Service provides core authentication, authorization, and multi-tenant management for the Tahoe SaaS product.

## Features

- Multi-tenant data isolation
- JWT-based authentication  
- Role-based access control
- API key management
- Session management with Redis
- Audit logging
- Rate limiting

## Quick Start

```bash
# Start infrastructure (PostgreSQL + Redis)
make infra-up

# Start platform service
make platform-up

# Check service status
make platform-status
```

## API Endpoints

- `GET /health` - Health check
- `GET /` - Service information
- `POST /api/v1/auth/login` - User login (coming in Phase 2)
- `POST /api/v1/auth/refresh` - Token refresh (coming in Phase 2)

## Technology Stack

- **Language**: TypeScript / Node.js
- **Framework**: Express.js
- **Database**: PostgreSQL (shared `tahoe` database)
- **ORM**: Prisma
- **Cache**: Redis (shared instance)
- **Container**: Docker

## Development

```bash
# Install dependencies (when developing locally)
npm install

# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev

# Build
npm run build

# Run tests
npm test
```

## Docker Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build
```

## Database Schema

The service includes the following models:
- `Tenant` - Organization/company accounts
- `User` - Individual users within tenants  
- `ApiKey` - API keys for service access
- `Session` - User sessions stored in Redis
- `FeatureFlag` - Per-tenant feature toggles
- `Event` - Audit and analytics events

## Phase 1 Status ✅

**Session 1: Service Setup & Database** - COMPLETED
- [x] Create platform service directory structure
- [x] Set up Docker configuration following Tahoe patterns  
- [x] Configure Prisma with shared database connection
- [x] Design schema to coexist with transcription tables
- [x] Implement base models (Tenant, User, ApiKey)
- [x] Write tests: Database connection, basic model creation
- [x] Complete and verify service starts correctly

## Next Steps (Phase 2)

- JWT token generation/validation
- Login/logout endpoints  
- Password hashing with bcrypt
- Session management in Redis
- Refresh token flow
- Role-based permission system
- API key generation for service access
- Rate limiting with Redis

## Service Integration

The platform service is designed to work with other Tahoe services:
- Runs on port 9200
- Connects to shared PostgreSQL database on tahoe-network
- Uses shared Redis instance for sessions and caching
- Provides authentication for transcription service
- Will integrate with agent-engine and loading services