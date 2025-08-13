# Tahoe Infrastructure Services

This directory contains the shared infrastructure services used by all microservices in the Project Tahoe monorepo.

## Services

### PostgreSQL (Port 5435)
- Shared database instance
- Each service uses its own schema:
  - `agent_engine` - Agent Engine service
  - `auth` - Authentication service (future)
  - `billing` - Billing service (future)

### Redis (Port 6382)
- Shared cache and session store
- Each service uses namespaced keys:
  - `agent-engine:*` - Agent Engine keys
  - `auth:*` - Authentication keys
  - `billing:*` - Billing keys

## Usage

### Start Infrastructure
```bash
cd services/infrastructure
docker-compose up -d
```

### Stop Infrastructure
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Access Databases
```bash
# PostgreSQL
psql postgresql://tahoe:tahoe@localhost:5435/tahoe

# Redis CLI
redis-cli -p 6382
```

### Debug Mode (with Redis Commander)
```bash
docker-compose --profile debug up -d
# Redis Commander available at http://localhost:8081
```

## Connection Strings

For local development, services connect using:
- PostgreSQL: `postgresql://tahoe:tahoe@localhost:5435/tahoe`
- Redis: `redis://localhost:6382`

For Docker-to-Docker communication:
- PostgreSQL: `postgresql://tahoe:tahoe@tahoe-postgres:5432/tahoe`
- Redis: `redis://tahoe-redis:6379`

## Data Persistence

Data is persisted in named Docker volumes:
- `tahoe_postgres_data` - PostgreSQL data
- `tahoe_redis_data` - Redis data

These volumes persist even when containers are stopped.