# Tahoe Infrastructure Service

This directory contains the shared infrastructure components for all Tahoe microservices, including PostgreSQL and Redis.

## Overview

The infrastructure service provides:
- **PostgreSQL Database**: Shared database server for all Tahoe services
- **Redis**: Shared cache and queue management for all Tahoe services  
- **Networking**: Shared Docker network for service communication

## Quick Start

1. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Start infrastructure services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are healthy:**
   ```bash
   docker-compose ps
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f
   ```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `POSTGRES_DB`: Database name (default: tahoe)
- `POSTGRES_USER`: Database user (default: tahoe_user)  
- `POSTGRES_PASSWORD`: Database password (default: tahoe_pass)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `REDIS_PORT`: Redis port (default: 6379)

### Database

- **Host**: `tahoe-postgres` (from other containers) or `localhost` (from host)
- **Port**: 5432 (configurable via POSTGRES_PORT)
- **Database**: `tahoe` (shared by all services)
- **Connection String**: `postgresql://tahoe_user:tahoe_pass@tahoe-postgres:5432/tahoe`

### Redis

- **Host**: `tahoe-redis` (from other containers) or `localhost` (from host)  
- **Port**: 6379 (configurable via REDIS_PORT)
- **Connection String**: `redis://tahoe-redis:6379`

## Service Communication

Services connect via the `tahoe-network` Docker network:

```yaml
networks:
  - tahoe-network
```

Use container hostnames for service-to-service communication:
- PostgreSQL: `tahoe-postgres:5432`
- Redis: `tahoe-redis:6379`

## Data Persistence

Data is persisted using Docker volumes:
- `tahoe_postgres_data`: PostgreSQL data
- `tahoe_redis_data`: Redis data

## Health Checks

Both services include health checks:
- PostgreSQL: `pg_isready` check every 30s
- Redis: `redis-cli ping` check every 30s

## Commands

```bash
# Start infrastructure
docker-compose up -d

# Stop infrastructure  
docker-compose down

# View service status
docker-compose ps

# View logs
docker-compose logs -f

# Reset data (WARNING: destroys all data)
docker-compose down -v
docker volume rm tahoe_postgres_data tahoe_redis_data

# Access PostgreSQL shell
docker exec -it tahoe-postgres psql -U tahoe_user -d tahoe

# Access Redis CLI  
docker exec -it tahoe-redis redis-cli
```

## Integration with Services

Services should configure their connections as:

```yaml
environment:
  - DATABASE_URL=postgresql://tahoe_user:tahoe_pass@tahoe-postgres:5432/tahoe
  - REDIS_URL=redis://tahoe-redis:6379
```

And reference the shared network:

```yaml
networks:
  - tahoe-network

networks:
  tahoe-network:
    external: true
```

## Redis Key Namespacing

Services should prefix their Redis keys with their service name to avoid conflicts:

- Platform service: `platform:*`
- Transcription service: `transcription:*`
- Agent engine: `agent_engine:*`
- Loading service: `loading:*`

## Development Workflow

1. Start infrastructure first: `docker-compose up -d`
2. Start individual services from their directories
3. Services will automatically connect to shared infrastructure
4. Stop individual services, keep infrastructure running across development sessions
5. Stop infrastructure when completely done: `docker-compose down`