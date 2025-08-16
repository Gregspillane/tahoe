# Tahoe Project

A microservices architecture for intelligent audio transcription and agent-based call analysis.

## Architecture Overview

Tahoe follows a microservices pattern with shared infrastructure:

```
tahoe/
├── infrastructure/          # Shared PostgreSQL + Redis
├── platform/               # Authentication, authorization & tenant management
├── transcribe/             # Transcription service with multi-provider processing
├── agent-engine/           # Agent-based call analysis (future)
└── loading/                # File ingestion service (future)
```

### Services

- **Infrastructure**: Shared PostgreSQL database and Redis cache/queue
- **Platform Service**: Authentication, authorization, and multi-tenant management
- **Transcription Service**: Multi-provider transcription with intelligent reconciliation
- **Agent Engine**: LLM-based call analysis (planned)
- **Loading Service**: MP3 file ingestion pipeline (planned)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Option 1: Using Make Commands (Recommended)

```bash
# Start all services
make all-up

# Check status
make infra-status
make platform-status
make transcribe-logs

# Stop all services
make all-down

# View all available commands
make help
```

### Option 2: Using Scripts

```bash
# Start all services
./scripts/start-services.sh

# Stop all services  
./scripts/stop-services.sh
```

### Option 3: Manual Setup

```bash
# Start infrastructure first
cd infrastructure
docker-compose up -d
cd ..

# Start platform service
cd platform
docker-compose up -d
cd ..

# Start transcription service
cd transcribe
docker-compose up -d
cd ..
```

## Services

### Infrastructure Service

**Location**: `infrastructure/`  
**Purpose**: Shared PostgreSQL database and Redis cache/queue

- **PostgreSQL**: `localhost:5432` (database: `tahoe`)
- **Redis**: `localhost:6379`
- **Network**: `tahoe-network`

See [infrastructure/README.md](infrastructure/README.md) for details.

### Transcription Service

**Location**: `transcribe/`  
**Purpose**: Multi-provider audio transcription with intelligent reconciliation

- **API**: `http://localhost:9100`
- **Features**: AssemblyAI + Google Speech + Gemini reconciliation
- **Queue**: Redis-based job processing with 4 workers

See [transcribe/README.md](transcribe/README.md) for details.

### Platform Service

**Location**: `platform/`  
**Purpose**: Authentication, authorization, and multi-tenant management

- **API**: `http://localhost:9200`
- **Features**: JWT authentication, API key management, tenant isolation
- **Database**: Uses shared PostgreSQL with platform-specific tables

See [platform/README.md](platform/README.md) for details.

## Development Workflow

### Daily Development

1. **Start infrastructure** (if not running):
   ```bash
   make infra-up
   ```

2. **Start services** you're working on:
   ```bash
   make platform-up
   make transcribe-up
   ```

3. **Work on your code** - services auto-reload on changes

4. **Stop services** when done:
   ```bash
   make all-down
   ```

### Full Reset (if needed)

```bash
# WARNING: This destroys all data
make reset
```

## Configuration

### Environment Files

Each service has its own `.env` file:

- `infrastructure/.env` - Database and Redis credentials
- `platform/.env` - JWT secrets and platform configuration
- `transcribe/.env` - API keys and service configuration

Copy `.env.example` files to `.env` and configure as needed.

### Database

All services share a single PostgreSQL database (`tahoe`) with separate schemas/tables per service.

### Redis Key Namespacing

Services use prefixed Redis keys to avoid conflicts:
- Platform: `platform:*`
- Transcription: `transcription:*`
- Agent Engine: `agent_engine:*` (planned)
- Loading: `loading:*` (planned)

## Monitoring

### Health Checks

- **Infrastructure**: `make infra-status`
- **Platform API**: `curl http://localhost:9200/health`
- **Transcription API**: `curl http://localhost:9100/health`
- **Detailed Status**: `curl http://localhost:9100/status`

### Logs

```bash
# Infrastructure logs
make infra-logs

# Platform service logs
make platform-logs

# Transcription service logs
make transcribe-logs

# Individual service logs
cd platform && docker-compose logs -f
cd transcribe && docker-compose logs -f
```

## API Usage

### Platform Service

```bash
# Health check
curl http://localhost:9200/health

# Authentication (get JWT token)
curl -X POST http://localhost:9200/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Get user profile (requires JWT token)
curl http://localhost:9200/api/v1/auth/me \
  -H "Authorization: Bearer <jwt_token>"

# API key management
curl http://localhost:9200/api/v1/api-keys \
  -H "Authorization: Bearer <jwt_token>"
```

### Transcription Service

```bash
# Health check
curl http://localhost:9100/health

# Submit job (test endpoint)
curl -X POST "http://localhost:9100/test/submit-job?audio_file_url=s3://bucket/file.mp3"

# Check job status
curl "http://localhost:9100/test/job-status/{job_id}"

# Detailed service status
curl http://localhost:9100/status
```

## Architecture Decisions

### Shared Infrastructure

- **Rationale**: Microservices share PostgreSQL and Redis to mirror production patterns
- **Benefits**: Easier management, cost efficiency, simplified deployment
- **Scaling**: Services can be scaled independently while sharing data stores

### Docker Networking

- **Network**: `tahoe-network` enables service-to-service communication
- **Service Discovery**: Services reference each other by container name
- **Port Mapping**: Standard ports exposed for local development

### Configuration Management

- **Environment Variables**: Service-specific `.env` files
- **Secrets**: API keys stored in environment, not in code
- **Defaults**: Sensible defaults for development use

## Troubleshooting

### Common Issues

1. **Port conflicts**: Stop existing services with `docker ps` and `docker stop`
2. **Database connection**: Ensure infrastructure is running first
3. **Network issues**: Recreate network with `make reset`

### Database Issues

```bash
# Check database connection
docker exec tahoe-postgres psql -U tahoe_user -d tahoe -c "SELECT 1"

# View database logs
cd infrastructure && docker-compose logs postgres
```

### Redis Issues

```bash
# Check Redis connection
docker exec tahoe-redis redis-cli ping

# View Redis logs
cd infrastructure && docker-compose logs redis
```

## Contributing

1. **Start with infrastructure**: Ensure `make infra-up` works
2. **Follow service patterns**: Use existing services as templates
3. **Add documentation**: Update README files for new services
4. **Test integration**: Verify services work together
5. **Update this README**: Document any new services or changes

## Project Status

- ✅ **Infrastructure Service**: Complete
- ✅ **Platform Service**: Complete (Authentication & Authorization)
- ✅ **Transcription Service**: Complete (Phase 5)
- 🔄 **Phase 6**: Service integration with platform authentication
- 📋 **Agent Engine**: Planned
- 📋 **Loading Service**: Planned