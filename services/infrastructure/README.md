# Tahoe Infrastructure Service

This service provides shared infrastructure components for the Tahoe monorepo, including:

- **PostgreSQL**: Primary database for all services
- **Redis**: Session storage and caching
- **Docker Networking**: Shared network for service communication
- **Service Orchestration**: Docker Compose configurations for all environments

## Quick Start

```bash
# From the infrastructure directory
cd services/infrastructure

# Setup development environment (first time)
make setup

# Start all services
make up

# Check health
make health

# View logs
make logs

# Stop services
make down
```

## Architecture

### Service Separation
- Each service in `services/` is independently deployable
- Infrastructure provides shared resources (database, cache, networking)
- Services connect to infrastructure via standard protocols (PostgreSQL, Redis)

### DNS/Domain Ready
- Each service configured for independent deployment
- Docker networking allows services to communicate by hostname
- Production ready for separate domain deployment

### Environment Configuration
- **Development**: `docker-compose.dev.yml` with hot reload and debug settings
- **Production**: `docker-compose.prod.yml` with optimized settings and scaling

## Services Provided

### PostgreSQL Database
- **Port**: 5432
- **Database**: tahoe
- **User**: tahoe_user
- **Container**: tahoe-postgres
- **Health Check**: Automatic readiness checks

### Redis Cache
- **Port**: 6379
- **Container**: tahoe-redis
- **Persistence**: AOF enabled
- **Health Check**: Redis ping command

### Docker Network
- **Name**: tahoe-network
- **Type**: Bridge network
- **Purpose**: Inter-service communication

## Service Integration

### Agent Engine Service
- Connects to PostgreSQL at `postgres:5432`
- Connects to Redis at `redis:6379`
- Exposes API on port 8001
- Self-contained service in `../agent-engine/`

### Future Services
Infrastructure ready to support additional services:
- Authentication Service
- API Gateway
- Monitoring Service
- etc.

## Database Management

```bash
# Connect to PostgreSQL
make db-shell

# Backup database
make db-backup

# Restore database
make db-restore BACKUP=backup_20231201_120000.sql

# View database logs
make logs-service SERVICE=postgres
```

## Redis Management

```bash
# Connect to Redis CLI
make redis-shell

# Flush all Redis data
make redis-flush

# View Redis logs
make logs-service SERVICE=redis
```

## Development

### Environment Files
- Root `.env`: Base configuration for all services
- `config/development.env`: Development overrides

### Hot Reload
Development mode mounts source code for real-time updates:
```bash
make dev  # Starts with development overrides
```

### Service Health
```bash
make health  # Check all services
```

## Production Deployment

### Build for Production
```bash
make prod  # Uses production configurations
```

### Scaling
Production compose file supports replica scaling:
```yaml
deploy:
  replicas: 3  # Multiple agent-engine instances
```

### Monitoring
Health checks built into all services for orchestration platforms.

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Stop conflicting services
   docker stop $(docker ps -q --filter "publish=5432" --filter "publish=6379")
   ```

2. **Clean Reset**
   ```bash
   make clean  # Remove all containers and volumes
   make setup  # Fresh start
   ```

3. **Service Dependencies**
   ```bash
   # Services start in dependency order
   # postgres -> redis -> agent-engine
   ```

4. **Logs Investigation**
   ```bash
   make logs                           # All services
   make logs-service SERVICE=postgres # Specific service
   ```

## Configuration

### Service Discovery
Services use Docker's built-in DNS:
- `postgres` resolves to PostgreSQL container
- `redis` resolves to Redis container
- `agent-engine` resolves to Agent Engine container

### Environment Variables
Infrastructure reads from root `.env` file:
```bash
# Database
POSTGRES_PASSWORD=your-secure-password

# Service Configuration
AGENT_ENGINE_LOG_LEVEL=INFO
GEMINI_API_KEY=your-api-key

# Security
SECRET_KEY=your-secret-key
```

This infrastructure service ensures all Tahoe services have reliable, scalable shared resources while maintaining service independence.