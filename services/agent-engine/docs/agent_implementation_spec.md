# Tahoe Agent Service - Implementation Specification

## Service Overview

**Service Name**: `agent-engine`  
**Purpose**: Core orchestration engine for multi-agent compliance analysis  
**Architecture Pattern**: Microservice with external state management  

## System Architecture

### Service Topology

```
┌─────────────────────────────────────────────────────┐
│                   agent-engine                        │
│  ┌─────────────────────────────────────────────┐    │
│  │          API Gateway (FastAPI)              │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │        Orchestration Engine (ADK)           │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │          Agent Registry & Factory           │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Redis     │  │   Postgres   │  │  Model APIs  │
│   (Cache)    │  │   (Prisma)   │  │   (Gemini)   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Data Models

### Database Schema (Postgres via Prisma)

```prisma
// Agent Configuration
model AgentTemplate {
  id              String   @id @default(uuid())
  name            String   @unique
  type            String   // "specialist" | "coordinator" | "aggregator"
  model           String   @default("gemini-2.0-flash")
  modelConfig     Json     // temperature, max_tokens, etc.
  capabilities    String[] // Array of capability tags
  tools           String[] // Tool identifiers
  triggerRules    Json     // Conditions for activation
  version         Int      @default(1)
  isActive        Boolean  @default(true)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  // Relations
  scorecardAgents ScorecardAgent[]
}

// Scorecard Configuration
model Scorecard {
  id              String   @id @default(uuid())
  name            String
  portfolioId     String
  version         Int      @default(1)
  requirements    Json     // Detailed requirement structure
  thresholds      Json     // Pass/fail/review thresholds
  isActive        Boolean  @default(true)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  // Relations
  portfolio       Portfolio @relation(fields: [portfolioId], references: [id])
  scorecardAgents ScorecardAgent[]
  analyses        Analysis[]
}

// Agent-Scorecard Mapping
model ScorecardAgent {
  id            String   @id @default(uuid())
  scorecardId   String
  agentId       String
  weight        Float    @default(1.0)
  isRequired    Boolean  @default(true)
  configuration Json?    // Override configuration
  
  // Relations
  scorecard     Scorecard     @relation(fields: [scorecardId], references: [id])
  agent         AgentTemplate @relation(fields: [agentId], references: [id])
  
  @@unique([scorecardId, agentId])
}

// Portfolio Configuration
model Portfolio {
  id            String   @id @default(uuid())
  organizationId String
  name          String
  configuration Json     // Portfolio-specific settings
  isActive      Boolean  @default(true)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  // Relations
  scorecards    Scorecard[]
  analyses      Analysis[]
}

// Analysis Results
model Analysis {
  id              String   @id @default(uuid())
  interactionId   String
  portfolioId     String
  scorecardId     String
  status          String   // "pending" | "processing" | "complete" | "failed"
  overallScore    Float?
  confidence      Float?
  results         Json     // Detailed analysis results
  agentOutputs    Json     // Individual agent outputs
  violations      Json[]   // Detected violations
  metadata        Json     // Execution metadata
  executionTime   Float?   // In seconds
  createdAt       DateTime @default(now())
  completedAt     DateTime?
  
  // Relations
  portfolio       Portfolio @relation(fields: [portfolioId], references: [id])
  scorecard       Scorecard @relation(fields: [scorecardId], references: [id])
  
  @@index([interactionId])
  @@index([portfolioId])
  @@index([status])
}
```

### Redis Cache Structure

```python
# Cache Patterns
cache_keys = {
    # Agent templates (TTL: 5 minutes)
    "agent:template:{agent_id}": AgentTemplate,
    
    # Scorecard configurations (TTL: 5 minutes)
    "scorecard:{scorecard_id}": Scorecard,
    
    # Portfolio settings (TTL: 10 minutes)
    "portfolio:{portfolio_id}": Portfolio,
    
    # Active analysis sessions (TTL: 30 minutes)
    "analysis:session:{analysis_id}": {
        "status": str,
        "phase": str,
        "agents_completed": list,
        "partial_results": dict,
        "started_at": datetime
    },
    
    # Model availability (TTL: 1 minute)
    "model:available:{model_name}": bool,
    
    # Rate limiting (TTL: 60 seconds)
    "ratelimit:{portfolio_id}": int
}
```

## Core Components

### 1. Orchestration Engine

```python
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import tool
import redis.asyncio as redis
from prisma import Prisma

class TahoeOrchestrator:
    def __init__(self):
        self.db = Prisma()
        self.cache = redis.Redis()
        self.agent_factory = AgentFactory()
        
    async def analyze_interaction(
        self, 
        interaction_data: dict,
        scorecard_id: str,
        portfolio_id: str,
        options: dict = None
    ) -> AnalysisResult:
        
        # Create analysis record
        analysis = await self.db.analysis.create({
            "data": {
                "interactionId": interaction_data["id"],
                "portfolioId": portfolio_id,
                "scorecardId": scorecard_id,
                "status": "processing"
            }
        })
        
        try:
            # Load scorecard configuration
            scorecard = await self.load_scorecard(scorecard_id)
            
            # Phase 1: Content Analysis
            content_metadata = await self.analyze_content(interaction_data)
            
            # Phase 2: Agent Selection
            required_agents = await self.select_agents(
                scorecard, 
                content_metadata,
                portfolio_id
            )
            
            # Phase 3: Build Execution Plan
            execution_plan = self.build_execution_plan(required_agents)
            
            # Phase 4: Execute Agents
            agent_results = await self.execute_agents(
                execution_plan,
                interaction_data,
                analysis.id
            )
            
            # Phase 5: Aggregate Results
            final_results = await self.aggregate_results(
                agent_results,
                scorecard
            )
            
            # Update analysis record
            await self.db.analysis.update({
                "where": {"id": analysis.id},
                "data": {
                    "status": "complete",
                    "overallScore": final_results.overall_score,
                    "confidence": final_results.confidence,
                    "results": final_results.to_dict(),
                    "agentOutputs": agent_results,
                    "violations": final_results.violations,
                    "completedAt": datetime.now()
                }
            })
            
            return final_results
            
        except Exception as e:
            await self.db.analysis.update({
                "where": {"id": analysis.id},
                "data": {
                    "status": "failed",
                    "metadata": {"error": str(e)}
                }
            })
            raise
    
    async def load_scorecard(self, scorecard_id: str) -> Scorecard:
        # Try cache first
        cached = await self.cache.get(f"scorecard:{scorecard_id}")
        if cached:
            return Scorecard.from_json(cached)
        
        # Load from database
        scorecard = await self.db.scorecard.find_unique({
            "where": {"id": scorecard_id},
            "include": {
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            }
        })
        
        # Cache for next time
        await self.cache.setex(
            f"scorecard:{scorecard_id}",
            300,  # 5 minutes
            scorecard.to_json()
        )
        
        return scorecard
    
    def build_execution_plan(self, agents: list) -> ExecutionPlan:
        # Analyze dependencies
        independent_agents = []
        dependent_agents = []
        
        for agent in agents:
            if agent.has_dependencies:
                dependent_agents.append(agent)
            else:
                independent_agents.append(agent)
        
        # Create execution plan
        plan = ExecutionPlan()
        
        # Parallel execution for independent agents
        if independent_agents:
            plan.add_phase(
                ParallelExecution(independent_agents)
            )
        
        # Sequential execution for dependent agents
        if dependent_agents:
            plan.add_phase(
                SequentialExecution(dependent_agents)
            )
        
        return plan
```

### 2. Agent Factory

```python
class AgentFactory:
    def __init__(self):
        self.db = Prisma()
        self.cache = redis.Redis()
        self.model_registry = ModelRegistry()
    
    async def create_agent(self, template_id: str) -> Agent:
        # Load template
        template = await self.load_template(template_id)
        
        # Get model configuration
        model_config = self.model_registry.get_config(
            template.model,
            template.modelConfig
        )
        
        # Create ADK agent
        agent = Agent(
            name=template.name,
            model=model_config.model_string,
            description=template.description,
            tools=await self.load_tools(template.tools),
            **model_config.parameters
        )
        
        return AgentWrapper(agent, template)
    
    async def load_template(self, template_id: str) -> AgentTemplate:
        # Check cache
        cached = await self.cache.get(f"agent:template:{template_id}")
        if cached:
            return AgentTemplate.from_json(cached)
        
        # Load from database
        template = await self.db.agenttemplate.find_unique({
            "where": {"id": template_id}
        })
        
        # Cache for reuse
        await self.cache.setex(
            f"agent:template:{template_id}",
            300,
            template.to_json()
        )
        
        return template
```

### 3. Model Registry

```python
class ModelRegistry:
    """Manages multiple model providers"""
    
    PROVIDERS = {
        "gemini": {
            "models": {
                "gemini-2.0-flash": {
                    "string": "gemini-2.0-flash",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                },
                "gemini-1.5-pro": {
                    "string": "gemini-1.5-pro",
                    "default_params": {
                        "temperature": 0.5,
                        "max_tokens": 4000
                    }
                }
            }
        },
        "openai": {
            "models": {
                "gpt-4-turbo": {
                    "string": "gpt-4-turbo-preview",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000
                    }
                }
            }
        },
        "anthropic": {
            "models": {
                "claude-3-opus": {
                    "string": "claude-3-opus-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_output_tokens": 2000
                    }
                }
            }
        }
    }
    
    def get_config(self, model_name: str, overrides: dict = None):
        # Parse provider from model name
        provider = self._get_provider(model_name)
        model_config = self.PROVIDERS[provider]["models"][model_name]
        
        # Merge with overrides
        params = {**model_config["default_params"]}
        if overrides:
            params.update(overrides)
        
        return ModelConfig(
            model_string=model_config["string"],
            parameters=params
        )
```

## API Specification

### Core Endpoints

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI(title="agent-engine")

# Request/Response Models
class AnalysisRequest(BaseModel):
    interaction: InteractionData
    scorecard_id: str
    portfolio_id: str
    options: dict = None

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    overall_score: float = None
    confidence: float = None
    categories: dict = None
    violations: list = None
    recommendations: list = None
    audit_trail: dict = None

# Endpoints
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_interaction(
    request: AnalysisRequest,
    auth: AuthContext = Depends(verify_service_token)
):
    """Submit interaction for analysis"""
    orchestrator = TahoeOrchestrator()
    result = await orchestrator.analyze_interaction(
        request.interaction,
        request.scorecard_id,
        request.portfolio_id,
        request.options
    )
    return AnalysisResponse.from_result(result)

@app.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    auth: AuthContext = Depends(verify_service_token)
):
    """Retrieve analysis results"""
    db = Prisma()
    analysis = await db.analysis.find_unique({
        "where": {"id": analysis_id}
    })
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    return analysis

@app.post("/agents/templates")
async def create_agent_template(
    template: AgentTemplateCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new agent template"""
    db = Prisma()
    agent = await db.agenttemplate.create({
        "data": template.dict()
    })
    return agent

@app.put("/agents/templates/{template_id}")
async def update_agent_template(
    template_id: str,
    updates: AgentTemplateUpdate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Update agent template"""
    db = Prisma()
    
    # Increment version on update
    current = await db.agenttemplate.find_unique({
        "where": {"id": template_id}
    })
    
    agent = await db.agenttemplate.update({
        "where": {"id": template_id},
        "data": {
            **updates.dict(exclude_unset=True),
            "version": current.version + 1
        }
    })
    
    # Invalidate cache
    cache = redis.Redis()
    await cache.delete(f"agent:template:{template_id}")
    
    return agent

@app.post("/scorecards")
async def create_scorecard(
    scorecard: ScorecardCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new scorecard"""
    db = Prisma()
    result = await db.scorecard.create({
        "data": scorecard.dict()
    })
    return result

@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "service": "agent-engine",
        "status": "healthy",
        "timestamp": datetime.now()
    }

@app.get("/metrics")
async def get_metrics():
    """Service metrics"""
    return {
        "analyses_in_progress": await get_active_analyses_count(),
        "cache_hit_rate": await get_cache_hit_rate(),
        "average_execution_time": await get_avg_execution_time()
    }
```

## Configuration Management

### Environment Configuration

```python
# config.py
from pydantic import BaseSettings

class ServiceConfig(BaseSettings):
    # Service Identity
    SERVICE_NAME: str = "agent-engine"
    SERVICE_TOKEN: str  # Internal auth token
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Model Providers
    GOOGLE_API_KEY: str = None
    OPENAI_API_KEY: str = None
    ANTHROPIC_API_KEY: str = None
    
    # Performance
    MAX_CONCURRENT_ANALYSES: int = 100
    AGENT_TIMEOUT_SECONDS: int = 30
    ANALYSIS_TIMEOUT_SECONDS: int = 300
    
    # Observability
    LOG_LEVEL: str = "INFO"
    TRACE_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
```

### Dynamic Configuration

```python
class ConfigurationManager:
    """Manages runtime configuration updates"""
    
    async def update_scorecard(self, scorecard_id: str, updates: dict):
        # Update in database
        await self.db.scorecard.update({
            "where": {"id": scorecard_id},
            "data": updates
        })
        
        # Invalidate cache
        await self.cache.delete(f"scorecard:{scorecard_id}")
        
        # Notify active analyses
        await self.notify_config_change("scorecard", scorecard_id)
    
    async def toggle_agent(self, agent_id: str, active: bool):
        # Update agent status
        await self.db.agenttemplate.update({
            "where": {"id": agent_id},
            "data": {"isActive": active}
        })
        
        # Clear cache
        await self.cache.delete(f"agent:template:{agent_id}")
```

## Deployment Configuration

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY prisma/ ./prisma/

# Generate Prisma client
RUN prisma generate

# Runtime configuration
ENV SERVICE_NAME=agent-engine
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Integration

```yaml
version: '3.8'

services:
  agent-engine:
    build: .
    container_name: agent-engine
    environment:
      - SERVICE_TOKEN=${SERVICE_TOKEN}
      - DATABASE_URL=postgresql://user:pass@postgres:5432/tahoe
      - REDIS_URL=redis://redis:6379
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - tahoe-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  tahoe-network:
    external: true
```

## Development Workflow

### Local Development Setup

```bash
# Project structure
agent-engine/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── orchestrator.py      # Core orchestration
│   ├── agents/
│   │   ├── factory.py       # Agent factory
│   │   ├── registry.py      # Agent registry
│   │   └── specialists/     # Specialist agents
│   ├── models/
│   │   ├── database.py      # Prisma models
│   │   ├── api.py           # Pydantic models
│   │   └── cache.py         # Cache schemas
│   ├── services/
│   │   ├── analysis.py      # Analysis service
│   │   ├── configuration.py # Config service
│   │   └── aggregation.py   # Result aggregation
│   └── utils/
│       ├── auth.py          # Authentication
│       ├── monitoring.py    # Metrics/tracing
│       └── errors.py        # Error handling
├── prisma/
│   └── schema.prisma        # Database schema
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Setup database
prisma db push

# Run migrations
prisma migrate dev

# Start development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/

# Format code
black src/ tests/
```

## Monitoring & Observability

### Key Metrics

```python
class MetricsCollector:
    """Collects and exposes service metrics"""
    
    metrics = {
        # Operational
        "analysis_requests_total": Counter(),
        "analysis_duration_seconds": Histogram(),
        "agent_execution_duration": Histogram(),
        "cache_hits_total": Counter(),
        "cache_misses_total": Counter(),
        
        # Business
        "analyses_by_portfolio": Counter(labels=["portfolio_id"]),
        "violations_detected": Counter(labels=["type"]),
        "confidence_scores": Histogram(),
        
        # System
        "active_analyses": Gauge(),
        "database_connections": Gauge(),
        "memory_usage_bytes": Gauge()
    }
```

### Tracing Implementation

```python
from opentelemetry import trace

tracer = trace.get_tracer("agent-engine")

class TracedOrchestrator:
    @tracer.start_as_current_span("analyze_interaction")
    async def analyze_interaction(self, ...):
        span = trace.get_current_span()
        span.set_attribute("interaction.id", interaction_id)
        span.set_attribute("scorecard.id", scorecard_id)
        
        # Trace each phase
        with tracer.start_as_current_span("content_analysis"):
            content = await self.analyze_content(...)
        
        with tracer.start_as_current_span("agent_selection"):
            agents = await self.select_agents(...)
        
        # Continue tracing...
```

## Extension Points

### Adding New Specialist Agents

```python
# 1. Define agent template in database
template = {
    "name": "new_specialist",
    "type": "specialist",
    "model": "gemini-2.0-flash",
    "capabilities": ["new_capability"],
    "tools": ["custom_tool_1"],
    "triggerRules": {
        "content_contains": ["keyword"],
        "scorecard_requires": ["capability"]
    }
}

# 2. Implement agent logic
class NewSpecialistAgent:
    async def analyze(self, interaction, context):
        # Custom analysis logic
        return SpecialistResult(...)

# 3. Register with factory
factory.register("new_specialist", NewSpecialistAgent)
```

### Custom Scorecard Types

```python
class CustomScorecard(BaseScorecard):
    """Extend base scorecard with custom logic"""
    
    async def select_agents(self, content_metadata):
        # Custom agent selection logic
        pass
    
    async def aggregate_results(self, agent_results):
        # Custom aggregation logic
        pass
```

## Performance Optimization

### Caching Strategy

```python
class CacheManager:
    """Intelligent caching with TTL management"""
    
    TTL_CONFIG = {
        "agent_template": 300,      # 5 minutes
        "scorecard": 300,           # 5 minutes
        "portfolio": 600,           # 10 minutes
        "analysis_session": 1800,   # 30 minutes
        "model_availability": 60    # 1 minute
    }
    
    async def get_or_load(self, key: str, loader_func):
        # Try cache
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # Load and cache
        data = await loader_func()
        ttl = self._get_ttl(key)
        await self.redis.setex(key, ttl, json.dumps(data))
        return data
```

### Parallel Processing

```python
class ParallelExecutor:
    """Manages parallel agent execution"""
    
    async def execute_parallel(self, agents: list, interaction: dict):
        # Create tasks for each agent
        tasks = []
        for agent in agents:
            task = asyncio.create_task(
                self._execute_with_timeout(agent, interaction)
            )
            tasks.append(task)
        
        # Wait for all with timeout
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle partial failures
        return self._process_results(results, agents)
```

## Next Steps for Implementation

### Component Priority Order

1. **Core Database Schema**
   - Set up Prisma schema
   - Create initial migrations
   - Seed with test data

2. **Basic Orchestration Engine**
   - Implement core orchestrator class
   - Add content analysis phase
   - Create simple agent selection logic

3. **Agent Factory & Registry**
   - Build agent template loader
   - Implement factory pattern
   - Create 2-3 basic specialist agents

4. **API Layer**
   - Set up FastAPI application
   - Implement authentication middleware
   - Create core endpoints

5. **Result Storage & Retrieval**
   - Implement analysis persistence
   - Add result aggregation logic
   - Create retrieval endpoints

6. **Caching Layer**
   - Add Redis integration
   - Implement cache patterns
   - Add cache invalidation

7. **Model Registry**
   - Add multi-model support
   - Implement fallback logic
   - Add model health checks

8. **Monitoring & Observability**
   - Add metrics collection
   - Implement tracing
   - Create health endpoints

This architecture provides the **flexibility and modularity** you need while keeping things **simple and maintainable**. The clear separation between configuration (database), execution (ADK agents), and caching (Redis) makes the system easy to understand and extend as requirements evolve.