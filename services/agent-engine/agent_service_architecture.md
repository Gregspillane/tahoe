# Project Tahoe - Agent Service Architecture

## Executive Summary

The Agent Service is the core intelligence layer of Project Tahoe, providing a flexible, configurable multi-agent orchestration platform for compliance auditing. Built on Google ADK, it offers dynamic agent composition, intelligent routing, and extensible analysis capabilities while maintaining simplicity through KISS principles.

## Service Overview

### Service Identity
- **Service Name**: `agent-engine`
- **Purpose**: Multi-agent orchestration for compliance analysis
- **Core Responsibility**: Coordinate specialized agents to analyze interactions against configurable compliance scorecards

### Key Design Principles
1. **Configuration-Driven**: Agents and workflows defined through database configuration, not code changes
2. **Stateless Execution**: Service remains stateless, leveraging external stores (Postgres/Redis) for state
3. **Observable by Default**: Comprehensive tracing and metrics for every operation
4. **Fail-Safe**: Graceful degradation when specialist agents fail
5. **Extensible**: Easy addition of new analysis domains without core changes
6. **Multi-Model Support**: Provider-agnostic design supporting Gemini, OpenAI, Anthropic, etc.

## Architecture Components

### 1. API Gateway Layer

```
External Requests → Authentication → Rate Limiting → Request Router
                         ↓
                  Internal Service Token
```

**Endpoints Structure:**
- `POST /analyze` - Submit interaction for analysis
- `GET /analysis/{id}` - Retrieve analysis results
- `POST /agents/configure` - Configure agent templates
- `GET /agents/available` - List available specialist agents
- `POST /scorecards` - Manage scorecaFrd templates
- `GET /health` - Service health check
- `GET /metrics` - Operational metrics

### 2. Core Orchestration Engine

```
Request → Content Analyzer → Agent Selector → Execution Planner
              ↓                    ↓               ↓
         Language/Type      Required Agents   Execution Graph
```

**Components:**

**Content Analyzer**
- Language detection
- Interaction type classification
- Complexity assessment
- Regulatory indicator detection

**Agent Selector**
- Rule-based selection based on content analysis
- Client-specific requirements overlay
- Confidence threshold evaluation
- Resource optimization

**Execution Planner**
- Dependency graph construction
- Parallel vs sequential determination
- Resource allocation
- Timeout management

### 3. Agent Registry & Factory

**Database-Driven Templates (Stored in Postgres via Prisma):**
```yaml
# Agent Template Structure
agent_template:
  id: "compliance_checker"
  type: "specialist"
  model: "gemini-2.0-flash"  # Configurable per template
  modelConfig:
    temperature: 0.3
    max_tokens: 2000
  capabilities:
    - fdcpa_compliance
    - reg_f_validation
  tools:
    - regulatory_database_search
    - violation_classifier
  triggers:
    - content_type: ["debt_collection", "financial"]
    - client_requirements: ["fdcpa_audit"]
  version: 1
  isActive: true
```

**Registry Features:**
- Dynamic agent registration via database
- Version management with history
- Capability indexing for selection
- Performance tracking per agent
- Model provider configuration
- Redis caching for performance

### 4. Execution Runtime

Using Google ADK patterns:

```python
# Simplified execution flow
class ComplianceOrchestrator:
    def __init__(self):
        self.router = RouterAgent(
            name="orchestrator",
            routing_strategy="dynamic"
        )
        self.registry = AgentRegistry()
    
    async def analyze(self, interaction, scorecard):
        # Phase 1: Content Analysis
        content_analysis = await self.content_analyzer.analyze(interaction)
        
        # Phase 2: Agent Selection
        required_agents = self.select_agents(
            content_analysis,
            scorecard.requirements
        )
        
        # Phase 3: Execution Planning
        execution_plan = self.plan_execution(required_agents)
        
        # Phase 4: Orchestrated Execution
        if execution_plan.can_parallelize:
            workflow = ParallelAgent(agents=required_agents)
        else:
            workflow = SequentialAgent(agents=required_agents)
        
        # Phase 5: Result Aggregation
        results = await workflow.run(interaction)
        return self.aggregate_results(results)
```

### 5. Configuration Management

**Three-Tier Configuration:**

1. **Global Configuration (Environment Variables)**
   - Service identity and tokens
   - Database and Redis connections
   - Model provider API keys
   - Default parameters and limits

2. **Portfolio Configuration (Database)**
   - Client-specific scorecards
   - Custom agent compositions
   - Override thresholds
   - Stored in Postgres, cached in Redis

3. **Request Configuration (API Payload)**
   - Per-request overrides
   - Priority settings
   - Debug flags

### 6. State & Session Management

**External State Management:**
- **Postgres (via Prisma)**: Persistent storage for:
  - Agent templates and versions
  - Scorecard configurations
  - Portfolio settings
  - Analysis results and audit trails
  
- **Redis**: High-performance caching for:
  - Active analysis sessions
  - Agent template cache (5-minute TTL)
  - Scorecard cache (5-minute TTL)
  - Portfolio settings cache (10-minute TTL)
  - Rate limiting counters

```python
# Session structure for complex analyses (stored in Redis)
session_schema = {
    "analysis_id": "uuid",
    "interaction_id": "reference",
    "portfolio_id": "reference",
    "status": "pending|processing|complete|failed",
    "state": {
        "phase": "content_analysis|agent_selection|execution|aggregation",
        "agents_completed": [],
        "agents_pending": [],
        "partial_results": {},
        "confidence_scores": {}
    },
    "metadata": {
        "start_time": "timestamp",
        "client_config": {},
        "trace_id": "uuid"
    }
}
```

## Data Flow Architecture

### Standard Analysis Flow

```
1. API Request (with interaction data)
        ↓
2. Authentication & Validation
        ↓
3. Content Pre-Processing
   - Transcription validation
   - Language detection
   - Speaker identification
        ↓
4. Orchestration Planning
   - Load scorecard requirements
   - Determine required agents
   - Build execution graph
        ↓
5. Agent Execution
   - Spawn specialist agents
   - Manage shared context
   - Monitor progress
        ↓
6. Result Aggregation
   - Collect agent outputs
   - Resolve conflicts
   - Calculate confidence
        ↓
7. Response Formation
   - Structure results
   - Generate audit trail
   - Return to caller
```

## Agent Types & Patterns

### 1. Coordinator Agent (Always Active)
- Routes to appropriate specialists based on database configuration
- Manages execution flow
- Handles error recovery

### 2. Specialist Agents (Dynamically Selected from Database)
```python
# Specialist agents defined in database, instantiated on-demand
specialist_types = {
    "compliance_analyst": {
        "focus": "regulatory_compliance",
        "model": "gemini-2.0-flash",  # Configurable per agent
        "tools": ["regulation_db", "violation_detector"]
    },
    "identity_verifier": {
        "focus": "authentication_protocols",
        "model": "gemini-2.0-flash",
        "tools": ["identity_patterns", "auth_validator"]
    },
    "quality_assessor": {
        "focus": "interaction_quality",
        "model": "gemini-1.5-pro",  # Can use different models
        "tools": ["sentiment_analyzer", "professionalism_scorer"]
    },
    "risk_evaluator": {
        "focus": "risk_indicators",
        "model": "gemini-2.0-flash",
        "tools": ["pattern_matcher", "risk_calculator"]
    }
}
```

### 3. Aggregator Agent (Result Processing)
- Combines specialist outputs
- Resolves conflicting findings
- Generates final scores
- Stores results in Postgres

## Scalability Strategy

### Horizontal Scaling
- Stateless service instances
- Load balancer distribution
- Shared configuration cache
- Distributed tracing

### Resource Management
```yaml
resource_limits:
  max_concurrent_analyses: 100
  max_agents_per_analysis: 10
  agent_timeout_seconds: 30
  total_analysis_timeout: 300
  
scaling_rules:
  cpu_threshold: 70
  memory_threshold: 80
  queue_depth_threshold: 50
  scale_up_increment: 2
  scale_down_delay: 300
```

## Security & Authentication

### Internal Service Communication
```python
# Service token validation
class ServiceAuthMiddleware:
    def validate_token(self, token):
        # Verify JWT signature
        # Check service identity
        # Validate permissions
        return authenticated_context
```

### Data Isolation
- Portfolio-level data segregation
- Encrypted sensitive content
- Audit trail preservation
- PII handling protocols

## Monitoring & Observability

### Key Metrics
```yaml
operational_metrics:
  - analysis_request_rate
  - analysis_completion_time
  - agent_execution_duration
  - confidence_score_distribution
  - error_rate_by_type

business_metrics:
  - analyses_per_portfolio
  - violation_detection_rate
  - human_review_triggers
  - scorecard_coverage

system_metrics:
  - agent_spawn_rate
  - memory_utilization
  - api_latency_p99
  - cache_hit_rate
```

### Tracing Strategy
- Trace ID propagation across all agents
- Detailed execution timeline
- Decision reasoning capture
- Performance bottleneck identification

## Configuration Examples

### Scorecard Configuration
```yaml
scorecard:
  id: "fdcpa_standard_v2"
  name: "FDCPA Compliance Standard"
  version: "2.0"
  
  requirements:
    - category: "identity_verification"
      weight: 0.2
      required_agents: ["identity_verifier"]
      
    - category: "disclosure_compliance"
      weight: 0.3
      required_agents: ["compliance_analyst"]
      
    - category: "communication_quality"
      weight: 0.15
      required_agents: ["quality_assessor"]
      
  thresholds:
    pass_score: 85
    review_trigger: 70
    high_risk: 50
```

### Agent Composition Configuration
```yaml
agent_composition:
  name: "debt_collection_analyzer"
  trigger_conditions:
    - interaction_type: "call"
    - detected_topics: ["payment", "debt", "collection"]
    
  agents:
    parallel:
      - compliance_analyst:
          focus: ["fdcpa", "reg_f"]
      - quality_assessor:
          metrics: ["tone", "professionalism"]
          
    sequential:
      - risk_evaluator:
          depends_on: ["compliance_analyst"]
          
  aggregation:
    strategy: "weighted_average"
    conflict_resolution: "highest_confidence"
```

## API Specification Examples

### Analysis Request
```json
POST /analyze
{
  "interaction": {
    "id": "call_123456",
    "type": "call",
    "transcript": "...",
    "metadata": {
      "duration": 300,
      "language": "en-US",
      "participants": 2
    }
  },
  "scorecard_id": "fdcpa_standard_v2",
  "portfolio_id": "portfolio_abc",
  "options": {
    "priority": "normal",
    "require_human_review": false
  }
}
```

### Analysis Response
```json
{
  "analysis_id": "analysis_789",
  "status": "complete",
  "overall_score": 87.5,
  "confidence": 0.92,
  "categories": {
    "identity_verification": {
      "score": 95,
      "findings": [...],
      "agent": "identity_verifier_v1"
    }
  },
  "violations": [],
  "recommendations": [],
  "audit_trail": {
    "agents_used": [...],
    "execution_time": 12.3,
    "trace_id": "..."
  }
}
```

## Deployment Architecture

### Container Structure
```dockerfile
# Base service container
FROM python:3.11-slim
WORKDIR /app

# Install ADK and dependencies
RUN pip install google-adk[full] prisma redis

# Copy service code
COPY src/ ./src/
COPY prisma/ ./prisma/

# Generate Prisma client
RUN prisma generate

# Runtime configuration
ENV SERVICE_NAME=agent-engine
ENV PORT=8000
ENV LOG_LEVEL=INFO

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
```

### Service Mesh Integration
```yaml
# Kubernetes service definition
apiVersion: v1
kind: Service
metadata:
  name: agent-engine
spec:
  selector:
    app: agent-engine
  ports:
    - port: 8000
      targetPort: 8000
  type: ClusterIP
```

## Evolution & Extension Points

### Phase 1: Core Capability
- Basic compliance analysis with 3-4 specialist agents
- Essential scorecard system stored in database
- Simple Redis caching
- Gemini model support

### Phase 2: Advanced Features
- Additional specialist agents via database configuration
- Dynamic scorecard builder
- Multi-model support (OpenAI, Anthropic)
- Enhanced caching strategies

### Phase 3: Intelligence Layer
- Pattern learning from human reviews
- Predictive risk scoring
- Automated threshold optimization
- Advanced result aggregation

### Phase 4: Platform Expansion
- Multi-modal analysis (video, images)
- Cross-interaction pattern detection
- Industry-specific agent marketplace
- Batch processing capabilities

## Risk Mitigation

### Technical Risks
- **Agent Failure**: Fallback chains and default responses
- **Timeout Issues**: Aggressive timeouts with partial result support
- **Resource Exhaustion**: Circuit breakers and rate limiting
- **Model Unavailability**: Multiple model fallbacks

### Business Risks
- **Incorrect Analysis**: Confidence scoring and human review triggers
- **Compliance Gaps**: Regular scorecard audits and updates
- **Performance Degradation**: Auto-scaling and performance monitoring

## Success Criteria

### Technical Metrics
- 99.9% API availability
- < 15 second p95 analysis time
- < 100ms API response time
- Zero data loss

### Business Metrics
- 95%+ accuracy vs human auditors
- 70% reduction in manual review
- 100% interaction coverage capability
- 10x cost efficiency improvement

## Next Steps

1. **Database Schema Setup**: Create Prisma schema for agent templates, scorecards, and results
2. **Core Orchestration Engine**: Build basic orchestrator with content analysis
3. **Agent Factory**: Implement database-driven agent instantiation
4. **API Implementation**: Develop RESTful endpoints with service token auth
5. **Redis Integration**: Add caching layer for performance
6. **Result Persistence**: Store analysis results in Postgres
7. **Testing Framework**: Unit and integration tests
8. **Documentation**: API docs and configuration guides