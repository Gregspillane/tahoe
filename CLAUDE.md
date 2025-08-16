# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Service Management (Makefile)
```bash
# Start all services
make all-up

# Start infrastructure only (PostgreSQL + Redis)
make infra-up

# Start individual services
make platform-up
make transcribe-up

# Check service status
make infra-status
make platform-status

# View logs
make infra-logs
make platform-logs
make transcribe-logs

# Stop services
make all-down
make platform-down
make transcribe-down

# Full reset (destroys all data)
make reset

# Basic connectivity tests
make test
```

### Platform Service (TypeScript/Node.js)
```bash
# Development (inside platform/ directory)
npm install
npm run build
npm run dev        # Development with hot reload
npm test           # Run Jest tests
npm run test:watch # Watch mode
npm run lint       # ESLint
npm run lint:fix   # Auto-fix linting issues

# Database operations
npm run prisma:generate  # Generate Prisma client
npm run prisma:migrate   # Run migrations (dev)
npm run prisma:deploy    # Deploy migrations (prod)
npm run prisma:studio    # Open Prisma Studio
```

### Transcription Service (Python/FastAPI)
```bash
# Development (inside transcribe/ directory)
pytest tests/      # Run Python tests
black .           # Code formatting
isort .           # Import sorting
mypy .            # Type checking

# Database operations
prisma generate   # Generate Prisma client
prisma db push    # Apply database changes
```

### Database Access
```bash
# Direct PostgreSQL access
docker exec -it tahoe-postgres psql -U tahoe_user -d tahoe

# Redis access
docker exec -it tahoe-redis redis-cli
```

## Architecture Overview

### Microservices Architecture
Tahoe follows a microservices pattern with shared infrastructure and service-to-service authentication:

**Services:**
- **Infrastructure** (port 5432/6379): Shared PostgreSQL + Redis
- **Platform Service** (port 9200): Authentication, authorization, multi-tenant management
- **Transcription Service** (port 9100): Multi-provider audio transcription with reconciliation
- **Agent Engine** (planned): LLM-based call analysis using Google ADK
- **Loading Service** (planned): File ingestion pipeline

**Technology Stack:**
- **Platform Service**: TypeScript/Node.js + Express + Prisma + PostgreSQL + Redis
- **Transcription Service**: Python/FastAPI + Prisma + PostgreSQL + Redis + AssemblyAI + Google Speech
- **Agent Engine**: Python + Google ADK (Gemini 2.5 Flash Lite)
- **Infrastructure**: PostgreSQL + Redis on Docker with tahoe-network

### Service Integration Pattern
All services share the same PostgreSQL database (`tahoe`) with tenant isolation:
- Platform Service handles authentication and tenant management
- Other services validate requests through Platform Service
- All data is tenant-scoped with `tenant_id` columns
- Redis used for sessions, caching, and job queues with service-specific prefixes

### Database Schema Design
The shared database uses tenant isolation with these key models:
- **Tenant**: Organization accounts with status, plan tier, settings
- **User**: Individual users within tenants with roles (ADMIN/MANAGER/USER)  
- **ApiKey**: Service access keys with scoped permissions
- **Session**: User sessions stored in both database and Redis
- **TranscriptionJob**: Audio transcription jobs with provider results
- **Event**: Audit and analytics events across all services

## Development Context

### Project Structure
```
tahoe/
├── infrastructure/          # Shared PostgreSQL + Redis
│   ├── docker-compose.yml
│   └── init.sql
├── platform/               # Authentication & tenant management (TypeScript)
│   ├── src/
│   ├── tests/
│   ├── package.json
│   ├── jest.config.js
│   └── docker-compose.yml
├── transcribe/             # Multi-provider transcription (Python)
│   ├── main.py
│   ├── workers/
│   ├── transcription/
│   ├── tests/
│   ├── requirements.txt
│   └── docker-compose.yml
├── agent-engine/           # Google ADK agents (planned)
└── scripts/               # Convenience scripts
    ├── start-services.sh
    └── stop-services.sh
```

### Current Development Status
- ✅ **Infrastructure**: Complete - PostgreSQL + Redis running
- ✅ **Platform Service**: Complete - Full auth/tenant management  
- ✅ **Transcription Service**: Complete - AssemblyAI + Google Speech integration
- 🔄 **Phase 6**: Service integration with platform authentication
- 📋 **Agent Engine**: Planned - Google ADK implementation
- 📋 **Loading Service**: Planned - File ingestion

### Multi-Tenant Architecture
Every service implements tenant isolation:
- All database queries automatically filtered by `tenant_id`
- Repository pattern enforces tenant context
- JWT tokens include tenant information
- API keys scoped to specific tenant permissions
- Redis keys prefixed by service and tenant

### Testing Philosophy
- Write tests immediately after implementing features
- Focus on integration tests over unit tests  
- Test happy paths first, edge cases later
- Use Jest + Supertest for Platform Service
- Use pytest for Transcription Service
- Test service-to-service communication

## Key Development Patterns

### Authentication Flow
1. External request → Platform Service validates JWT/API key
2. Platform Service returns tenant context and permissions
3. Target service receives request with tenant headers
4. All operations automatically scoped to tenant

### Service Communication
Services communicate via tahoe-network using:
- **External**: JWT tokens for user requests
- **Internal**: SERVICE_TOKEN + tenant context headers
- **Headers**: X-Tenant-ID, X-User-ID, X-Permissions

### Error Handling
- Structured logging with Winston (Platform) and structlog (Transcription)
- All errors include tenant context for debugging
- Service health checks available at `/health` endpoints
- Detailed status at `/status` endpoints

### Configuration Management
- Each service has `.env` files with service-specific settings
- Shared infrastructure uses common credentials
- All secrets managed via environment variables
- Docker Compose handles service dependencies

## API Testing

### Platform Service APIs
```bash
# Health check
curl http://localhost:9200/health

# User authentication
curl -X POST http://localhost:9200/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# API key management
curl http://localhost:9200/api/v1/api-keys \
  -H "Authorization: Bearer <jwt_token>"
```

### Transcription Service APIs  
```bash
# Health check
curl http://localhost:9100/health

# Service status (detailed)
curl http://localhost:9100/status

# Submit test job
curl -X POST "http://localhost:9100/test/submit-job?audio_file_url=s3://bucket/file.mp3"

# Check job status
curl "http://localhost:9100/test/job-status/{job_id}"
```

## Environment Setup

### Required Environment Variables

**Platform Service** (platform/.env):
```bash
DATABASE_URL=postgresql://tahoe_user:tahoe_pass@tahoe-postgres:5432/tahoe
REDIS_URL=redis://tahoe-redis:6379
JWT_SECRET=your-256-bit-secret
SERVICE_TOKEN=internal-service-secret
```

**Transcription Service** (transcribe/.env):
```bash  
DATABASE_URL=postgresql://tahoe_user:tahoe_pass@localhost:5433/tahoe
REDIS_URL=redis://localhost:6379
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
ASSEMBLYAI_API_KEY=...
GOOGLE_PROJECT_ID=...
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### Development Workflow
1. Start infrastructure: `make infra-up`
2. Start platform service: `make platform-up`  
3. Start transcription service: `make transcribe-up`
4. Test integration: `make test`
5. Check logs: `make platform-logs` or `make transcribe-logs`
6. Stop all: `make all-down`

## Memory Bank System
Each service maintains context and decisions in `/memory-bank/`:
- `context.md` - Current session state and handoffs
- `architecture.md` - Technical decisions and patterns
- `progress.md` - Development status tracking  
- `decisions.md` - Key project decisions log

## Google ADK Integration (Agent Engine)
The planned Agent Engine uses Google Agent Development Kit:
- **Model**: gemini-2.5-flash-lite (primary)
- **Structure**: Follow ADK documentation patterns exactly
- **Tools**: Use ADK's built-in tools before custom implementations
- **Documentation**: Reference `adk_docs_markdown/` for all decisions
- **Development**: Incremental approach following ADK quickstart patterns

## Production Considerations
- All services run in Docker containers
- Shared PostgreSQL database with tenant isolation
- Redis used for caching, sessions, and job queues
- Environment-specific configuration via .env files
- Health checks and monitoring endpoints available
- Structured logging for debugging and analytics