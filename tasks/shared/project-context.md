# Project Tahoe Agent Service - Persistent Context

## Service Identity
- **Name**: agent-engine
- **Purpose**: Multi-agent orchestration for compliance analysis
- **Domain**: agent.tahoe.com (local: http://localhost:8001)

## Architecture Patterns

### Database-First Design
All business logic, agent configurations, and workflows are stored in PostgreSQL via Prisma ORM. The service reads configurations from the database and executes them dynamically.

### Stateless Execution
The service maintains no internal state. All state is externalized to:
- **PostgreSQL**: Configurations, templates, results
- **Redis**: Sessions, caches, temporary data

### Agent Pattern
```python
# Standard agent result format
AgentResult:
  agent_name: str
  score: float (0-100)
  confidence: float (0-1)
  violations: List[Dict]
  recommendations: List[Dict]
  execution_time: float
```

### Cache Keys Pattern
```
agent:template:{id}     # TTL: 5 min
scorecard:{id}          # TTL: 5 min
portfolio:{id}          # TTL: 10 min
analysis:session:{id}   # TTL: 30 min
```

## Core Workflow

1. **Receive Interaction** → API endpoint accepts interaction data
2. **Content Analysis** → Determine interaction type and requirements
3. **Agent Selection** → Choose specialists based on scorecard rules
4. **Execution Planning** → Build parallel/sequential execution graph
5. **Agent Execution** → Run specialists with timeout management
6. **Result Aggregation** → Combine outputs using business rules
7. **Store Results** → Persist in PostgreSQL with audit trail

## Key Components

### Orchestrator (src/orchestrator.py)
- Central coordination of analysis workflow
- Manages agent selection and execution
- Handles session state in Redis

### Agent Factory (src/agents/factory.py)
- Creates agents from database templates
- Manages agent lifecycle and caching
- Wraps ADK agents with Tahoe interface

### Model Registry (src/models/registry.py)
- Multi-provider support (Gemini, OpenAI, Anthropic)
- Fallback handling and availability checking
- Configuration management per provider

### API Gateway (src/main.py)
- FastAPI application with middleware
- Authentication via service tokens
- Comprehensive error handling

## Database Tables

1. **AgentTemplate** - Agent configurations and prompts
2. **Scorecard** - Compliance requirements and rules
3. **ScorecardAgent** - Agent-to-scorecard mappings
4. **Portfolio** - Organization-specific settings
5. **Analysis** - Analysis results and metadata
6. **Tool** - Available tools for agents
7. **ModelProvider** - Model provider configurations

## Environment Variables

```bash
SERVICE_TOKEN=<internal-auth-token>
DATABASE_URL=postgresql://tahoe:tahoe@localhost:5435/tahoe
REDIS_URL=redis://localhost:6382
GOOGLE_API_KEY=<optional-for-gemini>
OPENAI_API_KEY=<optional-for-openai>
ANTHROPIC_API_KEY=<optional-for-anthropic>
```

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Real Google ADK and Gemini integration
- Focus on business logic correctness

### Integration Tests
- Test component interactions
- Use test database and cache
- Verify workflow execution

### Local Validation
- Everything must work in docker-compose first
- Use curl commands for API testing
- Seed data for realistic scenarios

## Common Patterns

### Error Handling
```python
try:
    result = await operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    # Update status in database
    # Clean up cache
    raise HTTPException(status_code=500, detail=str(e))
```

### Cache Pattern
```python
# Try cache first
cached = await cache.get(key)
if cached:
    return json.loads(cached)

# Load from database
data = await db.query()

# Cache for next time
await cache.setex(key, ttl, json.dumps(data))
return data
```

### Async Execution
```python
# Parallel execution
tasks = [agent.analyze(data) for agent in agents]
results = await asyncio.gather(*tasks, return_exceptions=True)

# Sequential with context
for agent in sequential_agents:
    result = await agent.analyze(data, context=previous_results)
    previous_results[agent.name] = result
```

## Development Commands

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Setup database
python -m prisma db push
python scripts/seed.py

# Run service
uvicorn src.main:app --reload --port 8001

# Test endpoint
curl http://localhost:8001/health
curl -X POST http://localhost:8001/analyze -d @sample.json

# Run tests
pytest tests/
```

## Implementation Priorities

1. **Make it work** - Basic functionality first
2. **Make it right** - Correct business logic
3. **Make it fast** - Optimize only when needed

## KISS Reminders

- No premature optimization
- No complex abstractions until needed
- Configuration over code
- Test locally before anything else
- Use existing libraries (ADK, Prisma, FastAPI)
- Focus on core workflow, not edge cases