# Configuration Management Guide

## Overview

Project Tahoe uses a **centralized configuration** approach with environment-specific overrides. All services read from a shared `.env` file at the monorepo root, with optional environment-specific overrides.

## Configuration Hierarchy

```
1. Base Configuration: /.env (required)
2. Environment Overrides: /config/{environment}.env (optional)
3. Runtime Environment Variables (highest priority)
```

## File Structure

```
tahoe/
├── .env                    # Main configuration (git-ignored)
├── .env.example           # Template with all variables
├── config/
│   ├── development.env    # Development overrides
│   ├── staging.env        # Staging overrides
│   └── production.env     # Production overrides
└── services/
    └── agent-engine/
        └── src/
            └── config.py  # Service configuration loader
```

## Configuration Loading

The configuration is loaded in this order:
1. **Base .env**: Loaded from project root
2. **Environment overrides**: Based on `ENVIRONMENT` variable
3. **Runtime variables**: Can override any setting

```python
# Automatic loading in config.py
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / ".env")  # Base config
load_dotenv(project_root / "config" / f"{environment}.env", override=True)  # Overrides
```

## Environment Variables

### Core Infrastructure

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Current environment | `development` | Yes |
| `DATABASE_HOST` | PostgreSQL host | `localhost` | Yes |
| `DATABASE_PORT` | PostgreSQL port | `5435` | Yes |
| `DATABASE_NAME` | Database name | `tahoe` | Yes |
| `DATABASE_USER` | Database user | `tahoe` | Yes |
| `DATABASE_PASSWORD` | Database password | `secure_password` | Yes |
| `REDIS_HOST` | Redis host | `localhost` | Yes |
| `REDIS_PORT` | Redis port | `6382` | Yes |

### Agent Engine Service

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `AGENT_ENGINE_PORT` | Service port | `8001` | Yes |
| `AGENT_ENGINE_SERVICE_TOKEN` | Internal auth token | `secure_token` | Yes |
| `AGENT_ENGINE_LOG_LEVEL` | Logging level | `INFO` | No |
| `AGENT_ENGINE_DATABASE_SCHEMA` | DB schema name | `agent_engine` | Yes |

### LLM Provider API Keys

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API | `AIza...` | Yes* |
| `OPENAI_API_KEY` | OpenAI API | `sk-...` | No |
| `ANTHROPIC_API_KEY` | Anthropic API | `sk-ant-...` | No |

*At least one LLM provider key is required

## Setting Up Configuration

### 1. Initial Setup

```bash
# Copy the template
cp .env.example .env

# Edit with your values
nano .env
```

### 2. Add Required Values

Edit `.env` and add:
- Database password
- Service tokens
- API keys (at least Google API key)

### 3. Environment-Specific Overrides

For development, staging, or production specific settings:

```bash
# Development overrides
nano config/development.env

# Example: Use debug logging in development
AGENT_ENGINE_LOG_LEVEL=DEBUG
```

## Service Configuration

Each service has its own `config.py` that:
1. Loads the centralized `.env`
2. Applies environment overrides
3. Provides typed configuration objects

```python
# services/agent-engine/src/config.py
from dotenv import load_dotenv

# Load centralized config
project_root = Path(__file__).parent.parent.parent.parent
load_dotenv(project_root / ".env")

# Load environment overrides
environment = os.getenv("ENVIRONMENT", "development")
load_dotenv(project_root / "config" / f"{environment}.env", override=True)

# Typed configuration
class ServiceConfig(BaseSettings):
    GOOGLE_API_KEY: Optional[str] = None
    DATABASE_PASSWORD: str
    # ... other fields
```

## Best Practices

### 1. Security
- **Never commit** `.env` files with real secrets
- Use **strong, unique** tokens for each service
- Rotate API keys and tokens regularly
- Use different keys for dev/staging/production

### 2. Organization
- Group related variables with comments
- Use consistent naming: `SERVICE_VARIABLE` format
- Document all variables in `.env.example`

### 3. Service Isolation
- Prefix service-specific vars: `AGENT_ENGINE_*`
- Each service gets its own database schema
- Services cannot access each other's config

### 4. Environment Management
```bash
# Development
ENVIRONMENT=development  # Uses config/development.env

# Staging
ENVIRONMENT=staging      # Uses config/staging.env

# Production
ENVIRONMENT=production   # Uses config/production.env
```

## Testing Configuration

### Verify Configuration Loading

```bash
# Test that configuration loads correctly
cd services/agent-engine
python -c "from src.config import settings; print(settings.GOOGLE_API_KEY[:10])"
```

### Test Gemini Integration

```bash
# Test LLM provider configuration
python scripts/test_gemini.py
```

Output should show:
- ✓ GOOGLE_API_KEY found
- ✓ Provider initialized successfully
- ✓ API key validated successfully

## Troubleshooting

### Configuration Not Loading

1. Check file exists: `ls -la /path/to/tahoe/.env`
2. Verify no syntax errors in .env
3. Check environment variable: `echo $ENVIRONMENT`

### Prisma Database URL

Prisma requires `DATABASE_URL` as environment variable:

```bash
# Export for Prisma CLI
export DATABASE_URL="postgresql://tahoe:password@localhost:5435/tahoe"

# Or add to .env
DATABASE_URL=postgresql://tahoe:password@localhost:5435/tahoe
```

### Service Can't Find Config

Ensure the service's `config.py`:
1. Calculates correct project root path
2. Calls `load_dotenv()` before creating config class
3. Uses correct environment variable names

## Adding New Services

When adding a new service:

1. **Define variables** in `.env.example`:
```bash
# New Service Configuration
NEW_SERVICE_PORT=8004
NEW_SERVICE_SERVICE_TOKEN=CHANGE_THIS
NEW_SERVICE_DATABASE_SCHEMA=new_service
```

2. **Create config.py** in the service:
```python
# services/new-service/src/config.py
# Copy pattern from agent-engine/src/config.py
```

3. **Use prefixed variables** to avoid conflicts:
- Good: `NEW_SERVICE_PORT`
- Bad: `PORT` (too generic)

## Production Deployment

For production:

1. Use **environment variables** instead of files
2. Store secrets in **secret management** (AWS Secrets, Vault)
3. Never use `.env` files on production servers
4. Set `ENVIRONMENT=production`

Example Kubernetes deployment:
```yaml
env:
  - name: GOOGLE_API_KEY
    valueFrom:
      secretKeyRef:
        name: api-keys
        key: google-api-key
  - name: DATABASE_PASSWORD
    valueFrom:
      secretKeyRef:
        name: database
        key: password
```

## Summary

- **Centralized**: Single `.env` at monorepo root
- **Hierarchical**: Base + environment overrides
- **Typed**: Pydantic models for validation
- **Secure**: Never commit real secrets
- **Scalable**: Easy to add new services/variables