# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Project Tahoe** is a distributed platform built as a monorepo with multiple independent microservices. Each service is completely self-contained, runs on its own DNS/domain, and communicates with other services via service-to-service authentication.

### Monorepo Structure
```
tahoe/                       # Monorepo root
├── .env                    # Centralized environment configuration
├── .env.example           # Template for all environments
├── config/                # Environment-specific overrides
│   ├── development.env    # Development settings
│   ├── staging.env        # Staging overrides
│   └── production.env     # Production overrides
├── services/
│   ├── agent-engine/       # Multi-agent orchestration service (agent.tahoe.com)
│   ├── tahoe-auth/         # (Future) Authentication service (auth.tahoe.com)
│   ├── tahoe-billing/      # (Future) Billing service (billing.tahoe.com)
│   └── ...                 # Each service is independent with its own DNS
├── infrastructure/         # Shared infrastructure configurations
│   ├── postgres/          # PostgreSQL configuration (shared instance, separate schemas)
│   ├── redis/             # Redis configuration (shared instance, namespaced keys)
│   └── docker-compose.yml # Infrastructure services setup
├── memory-bank/            # Cross-session documentation and context
└── CLAUDE.md              # This file
```

### Service Independence
- Each service is **completely self-contained** with its own:
  - API endpoints and authentication
  - Database schema (within shared PostgreSQL)
  - Cache namespace (within shared Redis)
  - Deployment configuration
  - DNS/domain (e.g., agent.tahoe.com, auth.tahoe.com)
- Services communicate via **service-to-service tokens**
- No centralized API gateway - each service exposes its own API
- **Centralized configuration**: All services use the monorepo root `.env` with service-specific prefixes

### Data Architecture
- **PostgreSQL**: Shared instance with service-specific schemas
  - `agent_engine` schema for agent-engine service
  - `auth` schema for auth service (future)
  - `billing` schema for billing service (future)
- **Redis**: Shared instance with namespaced keys
  - `agent-engine:*` keys for agent-engine
  - `auth:*` keys for auth service
  - Services cannot access each other's data directly

### agent-engine Service
The `agent-engine` service is the core intelligence layer providing multi-agent orchestration for compliance analysis. It operates independently at its own domain and coordinates specialized AI agents.

**Key Technologies (agent-engine)**:
- **Language**: Python 3.11
- **Framework**: FastAPI for API layer
- **Agent Framework**: Google ADK (Agent Development Kit)
- **Database**: PostgreSQL with Prisma ORM
- **Cache**: Redis
- **Models**: Gemini (primary), with support for OpenAI and Anthropic

## Core Development Principles

### Apply These Fundamental Guidelines
- **KISS (Keep It Simple, Stupid)**: Choose the most straightforward solution that works. Avoid unnecessary complexity. 
- **Incremental Progress**: Make small, testable changes rather than large sweeping modifications.
- **Configuration-Driven**: Agents and workflows are defined through database configuration, not code changes
- **Stateless Execution**: Service remains stateless, leveraging external stores (Postgres/Redis) for state

## Memory Bank System

The memory bank provides persistent context across sessions:

### Active Context
- **Location**: `/memory-bank/` - Contains living project documents
- **Key Files**:
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log

### Archived Documentation
- **Location**: `/memory-bank/archive/` - Completed plans and historical trackers
- Move documents here when they're no longer actively needed
- Maintain organized subdirectories by date or feature

### Using the Memory Bank
1. **Start of session**: Read `context.md` for current state
2. **During work**: Update relevant documents as you progress
3. **End of session**: Write handoff notes in `context.md`
4. **Major decisions**: Log in `decisions.md` with reasoning

## Development Workflow Guidelines

### Before Making Changes
1. **Understand the context**: Read relevant files and documentation
2. **Plan your approach**: Think through the implementation before coding
3. **Check for impacts**: Consider downstream effects of changes
4. **Validate assumptions**: Verify your understanding with the user when uncertain

### During Development
1. **Make incremental changes**: Small, focused commits
2. **Test as you go**: Verify each change works before moving on
3. **Document your reasoning**: Add comments for non-obvious decisions
4. **Keep the user informed**: Report progress and any issues encountered

### After Changes
1. **Verify functionality**: Ensure changes work as intended
2. **Check for regressions**: Confirm nothing else broke
3. **Update documentation**: Keep README and other docs current
4. **Clean up**: Remove debug code and temporary files

## Code Quality Standards

### General Best Practices
- Write clear, self-documenting code
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)
- Handle errors gracefully with proper error messages
- Add comments for complex logic or business rules
- Follow existing code patterns and conventions

### Testing Philosophy
- Write tests for critical functionality
- Test edge cases and error conditions
- Keep tests simple and readable
- Use descriptive test names that explain what's being tested
- Maintain test coverage without obsessing over percentages

### Performance Considerations
- Optimize only when necessary (measure first)
- Consider scalability in design decisions
- Be mindful of resource usage (memory, CPU, network)
- Cache expensive operations when appropriate
- Profile before optimizing

## Development Commands

### Infrastructure Setup
```bash
# 1. Setup centralized environment configuration
cp .env.example .env
# Edit .env with your secure values

# 2. Start shared infrastructure services (PostgreSQL & Redis)
cd infrastructure/
docker-compose up -d

# This starts:
# - PostgreSQL on port 5432
# - Redis on port 6379
```

### Working with Services
```bash
# Navigate to a specific service
cd services/agent-engine/

# Each service has its own dependencies and commands
```

### agent-engine Service Commands

#### Setup & Installation
```bash
cd services/agent-engine/

# Install Python dependencies
pip install google-adk[full] prisma redis fastapi uvicorn

# Setup Prisma database
prisma db push

# Run database migrations
prisma migrate dev
```

#### Development Server
```bash
# From services/agent-engine/
# Start development server with auto-reload
uvicorn src.main:app --reload --port 8001

# Run in production mode
uvicorn src.main:app --host 0.0.0.0 --port 8001
```

#### Testing
```bash
# From services/agent-engine/
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_orchestrator.py
```

#### Code Quality
```bash
# From services/agent-engine/
# Format code with Black
black src/ tests/

# Lint with ruff (if available)
ruff check src/

# Type checking with mypy (if configured)
mypy src/
```

#### Docker Operations
```bash
# From services/agent-engine/
# Build container
docker build -t agent-engine .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f agent-engine
```

## agent-engine Architecture

### Service Architecture
The `agent-engine` service is an independent microservice with:
- **Domain**: agent.tahoe.com (or configured subdomain)
- **Database**: `agent_engine` schema in shared PostgreSQL
- **Cache**: `agent-engine:*` namespace in shared Redis
- **Authentication**: Service-to-service token validation

### Core Components
1. **API Layer (FastAPI)** - RESTful API with service token authentication
2. **Orchestration Engine (ADK)** - Coordinates multi-agent workflows
3. **Agent Registry & Factory** - Database-driven agent instantiation
4. **Data Stores**:
   - PostgreSQL (via Prisma) - Uses `agent_engine` schema for configurations and results
   - Redis - Uses `agent-engine:*` namespace for caching and session management

### API Endpoints (agent-engine)
- `POST /analyze` - Submit interaction for compliance analysis (port 8001)
- `GET /analysis/{id}` - Retrieve analysis results
- `POST /agents/templates` - Create agent templates
- `PUT /agents/templates/{id}` - Update agent configurations
- `POST /scorecards` - Manage compliance scorecards
- `GET /health` - Service health check (http://localhost:8001/health)
- `GET /metrics` - Service metrics

### agent-engine File Structure
```
services/agent-engine/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── orchestrator.py      # Core orchestration logic
│   ├── agents/
│   │   ├── factory.py       # Agent instantiation from database
│   │   ├── registry.py      # Agent template management
│   │   └── specialists/     # Specialist agent implementations
│   ├── models/
│   │   ├── database.py      # Prisma model definitions (agent_engine schema)
│   │   ├── api.py           # Pydantic request/response models
│   │   └── cache.py         # Redis cache schemas (agent-engine:* keys)
│   └── services/
│       ├── analysis.py      # Analysis coordination
│       └── configuration.py # Dynamic configuration management
├── prisma/
│   └── schema.prisma        # agent_engine schema definition
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile               # Service-specific container
├── requirements.txt         # Python dependencies
└── .env.example            # Environment configuration template
```

### Cache Strategy
Redis caching with specific TTLs:
- Agent templates: 5 minutes
- Scorecards: 5 minutes  
- Portfolio settings: 10 minutes
- Active analysis sessions: 30 minutes

### Agent Execution Flow
1. Content Analysis - Analyze interaction type and requirements
2. Agent Selection - Choose required specialists based on scorecard
3. Execution Planning - Build parallel/sequential execution graph
4. Agent Execution - Run specialists with timeout management
5. Result Aggregation - Combine outputs and calculate scores
6. Persistence - Store results in PostgreSQL
- # Production Architecture Guidelines

We are building a production-ready service from day one. Our pre-launch status is an opportunity to establish clean architecture without technical debt.

## Core Principles

- **No Mocks or Workarounds**: Implement real solutions that will scale to production. Avoid temporary fixes or placeholder code.
- **Root Cause Focus**: Always address the underlying architectural issue rather than patching symptoms.
- **KISS with Sustainability**: Keep implementations simple while ensuring they're maintainable and extensible for long-term growth.
- **Fail Fast Philosophy**: No silent failures or fallback behaviors. Systems should fail explicitly and early when issues occur.
- **Clean Architecture First**: As a pre-launch application, prioritize establishing proper architectural patterns over quick feature delivery.

## Implementation Standards

- Build every component as if it's going into production tomorrow
- Design for observability and debugging from the start
- Ensure all error states are explicit and actionable
- Create clear separation of concerns in all architectural decisions