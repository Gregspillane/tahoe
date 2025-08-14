
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
**Tahoe** - SaaS platform for the banking and financial industry, supporting multiple compliance use cases. Built as a monorepo with multiple services.

### Key Services
- **agent-engine**: The "brains" of the platform - Universal agent orchestration using Google ADK for dynamic agent composition with specification-driven architecture. Self-contained with its own PostgreSQL and Redis.
- **billing**: Usage tracking and subscription management (planned - will have its own infrastructure)
- **auth**: Authentication and authorization service (planned - will have its own infrastructure)  
- **frontend**: Dashboard and user interface (planned)

## Development Commands

### Local Development
```bash
# Install dependencies
cd services/agent-engine
pip install -r requirements.txt

# Run development server (with hot reload)
make dev  # Runs on port 8001

# Run tests
make test
pytest tests/ -v  # Verbose test output

# Validate ADK patterns
make validate
python scripts/validate_adk_patterns.py

# Check linting/formatting
ruff check src/
ruff format src/
```

### Docker Development
```bash
# Start complete agent-engine environment (PostgreSQL, Redis, Agent-Engine)
cd services/agent-engine
make docker-up

# View logs
make docker-logs  # All service logs

# Stop services
make docker-down

# Clean up (remove volumes)
make clean
```

### Database Management
```bash
# Run Prisma migrations
cd services/agent-engine
npx prisma migrate dev  # Development
npx prisma migrate deploy  # Production

# Generate Prisma client
npx prisma generate

# Open Prisma Studio
npx prisma studio
```

## Architecture Overview

### Platform Architecture
Tahoe is a microservices-based SaaS platform designed for banking and financial compliance. Each service runs independently but shares centralized configuration and secret management. The agent-engine service provides the AI/ML capabilities that power compliance workflows across the platform.

### Configuration & Deployment Strategy

#### Environment-Aware Configuration
The system is fully environment-aware with no hardcoded URLs or paths:

| Environment | Service URLs | Config Source | Secrets |
|------------|--------------|---------------|---------|
| Development | `localhost:8001` (agent-engine)<br>`localhost:8002` (auth)<br>`localhost:8003` (billing) | Root `.env` file | `.env` file |
| Staging | `agent-engine.staging.tahoe.com`<br>`auth.staging.tahoe.com`<br>`billing.staging.tahoe.com` | Helm charts in `helm/configs/` | HashiCorp Vault |
| Production | `agent-engine.tahoe.com`<br>`auth.tahoe.com`<br>`billing.tahoe.com` | Helm charts in `helm/configs/` | HashiCorp Vault |

#### Configuration Hierarchy
```
Development:
  tahoe/.env → Environment variables → Service defaults

Staging/Production:
  Vault secrets → Helm values (helm/values/) → Environment variables → Service defaults
```

#### Configuration Sources by Environment
- **Development**: Root `.env` file only (all config in one place)
- **Staging**: Helm charts + `helm/values/staging.yaml` + Vault secrets
- **Production**: Helm charts + `helm/values/production.yaml` + Vault secrets

#### Service Independence
- Each service can run standalone with its configuration subset
- Services discover each other via environment-specific URLs
- No direct service-to-service file dependencies
- Shared resources (DB, Redis) accessed via configured endpoints

### Agent-Engine Design Principles
1. **Specification-Driven**: All agents, workflows, and tools defined via YAML/JSON specifications in `specs/` directory
2. **Universal Agent Factory**: Single factory creates all ADK agent types (LlmAgent, Sequential, Parallel, Loop, Custom)
3. **Environment-Aware Config**: No hardcoded URLs - uses Pydantic Settings with environment detection
4. **Plugin-Based Tools**: Runtime tool registration with automatic ADK function wrapping

### Environment Variables Pattern
```python
# Service discovery (automatically set based on ENVIRONMENT)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")  
# Development: http://localhost:8002
# Staging: https://auth.staging.tahoe.com
# Production: https://auth.tahoe.com

# Service-specific configs use prefixes
AGENT_ENGINE_PORT = 8001
AGENT_ENGINE_LOG_LEVEL = "INFO"
AUTH_SERVICE_PORT = 8002
BILLING_SERVICE_PORT = 8003

# Shared infrastructure (no prefix)
DATABASE_HOST = "localhost"  # or RDS endpoint
REDIS_HOST = "localhost"     # or ElastiCache endpoint
```

### Critical ADK Patterns (MUST FOLLOW)
```python
# ✅ CORRECT Agent Naming - Python identifiers only
agent = LlmAgent(name="content_analyzer")  # Underscores, not hyphens

# ✅ CORRECT Session Access - Property, not method
runner = InMemoryRunner(agent, app_name="tahoe")
session_service = runner.session_service  # Property access

# ✅ CORRECT LoopAgent Structure - List parameter
loop_agent = LoopAgent(sub_agents=[agent1, agent2])  # List, not single

# ✅ CORRECT Tool Wrapping - Automatic preferred
def my_tool(x: int) -> int:
    return x * 2

agent = LlmAgent(tools=[my_tool])  # Automatic wrapping
# Use FunctionTool only when explicit control needed

# ✅ CORRECT Workflow Agents - Separate instances
workflow = SequentialAgent(
    sub_agents=[
        LlmAgent(name="step1", ...),  # New instance
        LlmAgent(name="step2", ...)   # New instance
    ]
)
```

### Anti-Patterns to AVOID
- ❌ Don't use hyphens in agent names: `LlmAgent(name="content-analyzer")`
- ❌ Don't call session_service as method: `runner.session_service()`
- ❌ Don't use `sub_agent` in LoopAgent: `LoopAgent(sub_agent=agent)`
- ❌ Don't reuse agent instances across workflows
- ❌ Don't implement custom runners (use InMemoryRunner)

### Monorepo Structure
```
tahoe/                       # Tahoe platform monorepo
├── services/
│   ├── agent-engine/        # Self-contained AI orchestration service (port 8001)
│   │   ├── src/
│   │   │   ├── core/       # Agent factory, workflow engine, sessions
│   │   │   ├── api/        # FastAPI endpoints
│   │   │   └── services/   # Business logic
│   │   ├── specs/          # Agent/workflow/tool specifications
│   │   ├── config/         # Service-specific settings
│   │   ├── prisma/         # Database schemas and migrations
│   │   └── docker-compose.yml  # PostgreSQL, Redis, Agent-Engine
│   ├── auth/              # Authentication service (planned - self-contained)
│   ├── billing/           # Billing service (planned - self-contained)
│   └── frontend/          # Dashboard UI (planned)
├── helm/                 # Kubernetes deployment (staging/prod)
│   ├── charts/           # Helm charts for each service
│   │   ├── agent-engine/
│   │   ├── auth/
│   │   └── billing/
│   └── values/           # Environment-specific values
│       ├── staging.yaml
│       └── production.yaml
├── memory-bank/          # Platform-wide documentation
├── tasks/                # Development tasks (R1-R7 releases)
└── .env                  # Centralized secrets/config (development only)
```

## Memory Bank System
- **Active context**: `/memory-bank/` - Living project documents
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions  
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log
- **Archived docs**: `/memory-bank/archive/` - Completed plans

## Google ADK Documentation
When encountering ADK-related issues, consult official documentation first:
- Main Docs: https://google.github.io/adk-docs/
- GitHub: https://github.com/google/adk-python
- API Reference: https://google.github.io/adk-docs/api-reference/python/

## Development Philosophy
- KISS: Keep implementations simple and straightforward
- Fail fast with clear error messages
- Local dev environment mirrors production
- Clean code over backwards compatibility (pre-launch)
- gemini-2.5-flash-lite is the initial model we are going to use. It does exists. Dont change it.
- Avoid fallbacks. Use a fail-fast approach—either it works or it doesn’t. Fallbacks create a false sense of security and make real bugs harder to detect.