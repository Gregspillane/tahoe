# Project Tahoe - Agent Service Masterplan

## Claude Code Memory Reference

This document serves as the definitive architectural and implementation reference for Project Tahoe's agent-engine service. All development should reference this masterplan for consistency and autonomous implementation guidance.

---

## Executive Summary

**Service Name**: `agent-engine`  
**Purpose**: Core multi-agent orchestration platform for compliance auditing  
**Architecture**: Microservice built on Google ADK with external state management  
**Development Approach**: Configuration-driven, database-first, stateless execution  

### Claude Code Implementation Context
- **Single Session Scope**: Core service framework and basic orchestration
- **Multi-Session Scope**: Complete agent ecosystem with all specialist agents
- **Autonomous Execution**: Service designed for independent Claude Code development with minimal human intervention

---

## Service Architecture Overview

### Core Design Philosophy
1. **Configuration-Driven Development**: Agents, workflows, and business logic defined in database, not hardcoded
2. **Stateless Autonomous Operation**: Service maintains no internal state, enabling rapid development and deployment
3. **Database-First Architecture**: Postgres via Prisma as single source of truth for all configuration
4. **External State Management**: Redis for high-performance caching and session management
5. **Observable by Default**: Comprehensive tracing, metrics, and audit trails for every operation
6. **Multi-Model Provider Support**: Provider-agnostic design supporting Gemini, OpenAI, Anthropic

### System Topology

```
┌─────────────────────────────────────────────────────┐
│                   agent-engine                        │
│  ┌─────────────────────────────────────────────┐    │
│  │          API Gateway (FastAPI)              │    │
│  │          - Authentication                   │    │
│  │          - Rate Limiting                    │    │
│  │          - Request Validation               │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │        Orchestration Engine (ADK)           │    │
│  │        - Content Analysis                   │    │
│  │        - Agent Selection                    │    │
│  │        - Execution Planning                 │    │
│  │        - Result Aggregation                 │    │
│  └─────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────┐    │
│  │          Agent Registry & Factory           │    │
│  │          - Template Management              │    │
│  │          - Dynamic Instantiation            │    │
│  │          - Performance Tracking             │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│    Redis     │  │   Postgres   │  │  Model APIs  │
│   (Cache &   │  │   (Prisma)   │  │   (Gemini    │
│   Sessions)  │  │              │  │  OpenAI, etc)│
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Database Schema (Postgres via Prisma)

### Complete Schema Definition

```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-py"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Agent Configuration
model AgentTemplate {
  id              String   @id @default(uuid())
  name            String   @unique
  description     String?
  type            String   // "specialist" | "coordinator" | "aggregator"
  model           String   @default("gemini-2.0-flash")
  modelConfig     Json     // temperature, max_tokens, etc.
  capabilities    String[] // Array of capability tags
  tools           String[] // Tool identifiers
  triggerRules    Json     // Conditions for activation
  systemPrompt    String?  // Custom system prompt
  userPrompt      String?  // Custom user prompt template
  version         Int      @default(1)
  isActive        Boolean  @default(true)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  // Relations
  scorecardAgents ScorecardAgent[]
  
  @@map("agent_templates")
}

// Scorecard Configuration
model Scorecard {
  id              String   @id @default(uuid())
  name            String
  description     String?
  portfolioId     String
  version         Int      @default(1)
  requirements    Json     // Detailed requirement structure
  thresholds      Json     // Pass/fail/review thresholds
  aggregationRules Json    // How to combine agent results
  isActive        Boolean  @default(true)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
  
  // Relations
  portfolio       Portfolio @relation(fields: [portfolioId], references: [id])
  scorecardAgents ScorecardAgent[]
  analyses        Analysis[]
  
  @@map("scorecards")
}

// Agent-Scorecard Mapping
model ScorecardAgent {
  id            String   @id @default(uuid())
  scorecardId   String
  agentId       String
  weight        Float    @default(1.0)
  isRequired    Boolean  @default(true)
  configuration Json?    // Override configuration
  executionOrder Int?    // For sequential execution
  
  // Relations
  scorecard     Scorecard     @relation(fields: [scorecardId], references: [id])
  agent         AgentTemplate @relation(fields: [agentId], references: [id])
  
  @@unique([scorecardId, agentId])
  @@map("scorecard_agents")
}

// Portfolio Configuration
model Portfolio {
  id            String   @id @default(uuid())
  organizationId String
  name          String
  description   String?
  configuration Json     // Portfolio-specific settings
  isActive      Boolean  @default(true)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  // Relations
  scorecards    Scorecard[]
  analyses      Analysis[]
  
  @@map("portfolios")
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
  recommendations Json[]   // Suggested actions
  metadata        Json     // Execution metadata
  executionTime   Float?   // In seconds
  traceId         String?  // Distributed tracing ID
  createdAt       DateTime @default(now())
  completedAt     DateTime?
  
  // Relations
  portfolio       Portfolio @relation(fields: [portfolioId], references: [id])
  scorecard       Scorecard @relation(fields: [scorecardId], references: [id])
  
  @@index([interactionId])
  @@index([portfolioId])
  @@index([status])
  @@index([createdAt])
  @@map("analyses")
}

// Tool Configuration
model Tool {
  id            String   @id @default(uuid())
  name          String   @unique
  description   String?
  type          String   // "function" | "api" | "database"
  configuration Json     // Tool-specific config
  isActive      Boolean  @default(true)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  @@map("tools")
}

// Model Provider Configuration
model ModelProvider {
  id            String   @id @default(uuid())
  name          String   @unique // "gemini" | "openai" | "anthropic"
  baseUrl       String?
  apiKeyEnvVar  String   // Environment variable name
  models        Json     // Available models and configurations
  isActive      Boolean  @default(true)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  @@map("model_providers")
}
```

### Key Database Patterns

1. **Configuration Versioning**: All major entities track versions for rollback capability
2. **Soft Deletion**: Use `isActive` flags rather than hard deletes
3. **JSON Configuration**: Flexible configuration storage for evolving requirements
4. **Audit Trails**: Comprehensive timestamps and metadata tracking
5. **Relationship Mapping**: Clear foreign key relationships for data integrity

---

## Redis Cache Architecture

### Cache Structure and Patterns

```python
# Cache key patterns with TTL strategies
CACHE_PATTERNS = {
    # Agent templates (TTL: 5 minutes)
    "agent:template:{agent_id}": {
        "ttl": 300,
        "data": "AgentTemplate object"
    },
    
    # Scorecard configurations (TTL: 5 minutes)
    "scorecard:{scorecard_id}": {
        "ttl": 300,
        "data": "Scorecard with agents"
    },
    
    # Portfolio settings (TTL: 10 minutes)
    "portfolio:{portfolio_id}": {
        "ttl": 600,
        "data": "Portfolio configuration"
    },
    
    # Active analysis sessions (TTL: 30 minutes)
    "analysis:session:{analysis_id}": {
        "ttl": 1800,
        "data": {
            "status": "pending|processing|complete|failed",
            "phase": "content_analysis|agent_selection|execution|aggregation",
            "agents_completed": [],
            "agents_pending": [],
            "partial_results": {},
            "confidence_scores": {},
            "started_at": "timestamp",
            "trace_id": "uuid"
        }
    },
    
    # Model availability (TTL: 1 minute)
    "model:available:{model_name}": {
        "ttl": 60,
        "data": "boolean"
    },
    
    # Rate limiting (TTL: 60 seconds)
    "ratelimit:{portfolio_id}:{window}": {
        "ttl": 60,
        "data": "request_count"
    },
    
    # Agent performance metrics (TTL: 5 minutes)
    "metrics:agent:{agent_id}": {
        "ttl": 300,
        "data": {
            "avg_execution_time": "float",
            "success_rate": "float",
            "last_updated": "timestamp"
        }
    }
}
```

---

## Core Implementation Components

### 1. Orchestration Engine

```python
# src/orchestrator.py
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import tool
import redis.asyncio as redis
from prisma import Prisma
from typing import Dict, List, Optional
import asyncio
import json
import uuid
from datetime import datetime

class TahoeOrchestrator:
    """Core orchestration engine for multi-agent compliance analysis"""
    
    def __init__(self):
        self.db = Prisma()
        self.cache = redis.Redis()
        self.agent_factory = AgentFactory()
        self.content_analyzer = ContentAnalyzer()
        self.result_aggregator = ResultAggregator()
        
    async def analyze_interaction(
        self, 
        interaction_data: dict,
        scorecard_id: str,
        portfolio_id: str,
        options: dict = None
    ) -> AnalysisResult:
        """
        Main entry point for interaction analysis
        
        Args:
            interaction_data: The interaction to analyze (call transcript, etc.)
            scorecard_id: Which scorecard to use for analysis
            portfolio_id: Portfolio context for configuration
            options: Additional analysis options
            
        Returns:
            AnalysisResult with scores, violations, and recommendations
        """
        
        # Generate trace ID for monitoring
        trace_id = str(uuid.uuid4())
        
        # Create analysis record
        analysis = await self.db.analysis.create({
            "data": {
                "interactionId": interaction_data["id"],
                "portfolioId": portfolio_id,
                "scorecardId": scorecard_id,
                "status": "processing",
                "traceId": trace_id,
                "metadata": {
                    "options": options or {},
                    "interaction_type": interaction_data.get("type", "unknown")
                }
            }
        })
        
        try:
            # Store session in Redis for monitoring
            await self.cache.setex(
                f"analysis:session:{analysis.id}",
                1800,  # 30 minutes
                json.dumps({
                    "status": "processing",
                    "phase": "initialization",
                    "started_at": datetime.now().isoformat(),
                    "trace_id": trace_id
                })
            )
            
            # Phase 1: Content Analysis
            content_metadata = await self.analyze_content(
                interaction_data, 
                analysis.id
            )
            
            # Phase 2: Load Scorecard and Select Agents
            scorecard = await self.load_scorecard(scorecard_id)
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
                analysis.id,
                trace_id
            )
            
            # Phase 5: Aggregate Results
            final_results = await self.aggregate_results(
                agent_results,
                scorecard,
                analysis.id
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
                    "recommendations": final_results.recommendations,
                    "executionTime": final_results.execution_time,
                    "completedAt": datetime.now()
                }
            })
            
            # Clean up session cache
            await self.cache.delete(f"analysis:session:{analysis.id}")
            
            return final_results
            
        except Exception as e:
            await self.db.analysis.update({
                "where": {"id": analysis.id},
                "data": {
                    "status": "failed",
                    "metadata": {
                        "error": str(e),
                        "trace_id": trace_id
                    }
                }
            })
            
            # Clean up session cache
            await self.cache.delete(f"analysis:session:{analysis.id}")
            raise
    
    async def analyze_content(self, interaction_data: dict, analysis_id: str) -> dict:
        """Analyze interaction content to determine processing requirements"""
        
        await self._update_session_phase(analysis_id, "content_analysis")
        
        content_metadata = {
            "language": self.content_analyzer.detect_language(interaction_data),
            "interaction_type": interaction_data.get("type", "unknown"),
            "duration": interaction_data.get("metadata", {}).get("duration"),
            "participant_count": interaction_data.get("metadata", {}).get("participants", 1),
            "detected_topics": await self.content_analyzer.extract_topics(interaction_data),
            "regulatory_indicators": await self.content_analyzer.detect_regulatory_context(interaction_data),
            "complexity_score": await self.content_analyzer.assess_complexity(interaction_data)
        }
        
        return content_metadata
    
    async def load_scorecard(self, scorecard_id: str) -> dict:
        """Load scorecard configuration with caching"""
        
        # Try cache first
        cached = await self.cache.get(f"scorecard:{scorecard_id}")
        if cached:
            return json.loads(cached)
        
        # Load from database with relationships
        scorecard = await self.db.scorecard.find_unique({
            "where": {"id": scorecard_id},
            "include": {
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            }
        })
        
        if not scorecard:
            raise ValueError(f"Scorecard {scorecard_id} not found")
        
        # Cache for next time
        await self.cache.setex(
            f"scorecard:{scorecard_id}",
            300,  # 5 minutes
            json.dumps(scorecard, default=str)
        )
        
        return scorecard
    
    async def select_agents(
        self, 
        scorecard: dict, 
        content_metadata: dict, 
        portfolio_id: str
    ) -> List[dict]:
        """Select required agents based on scorecard and content analysis"""
        
        required_agents = []
        
        for scorecard_agent in scorecard["scorecardAgents"]:
            agent_template = scorecard_agent["agent"]
            
            # Check if agent should be activated based on trigger rules
            if self._should_activate_agent(agent_template, content_metadata):
                required_agents.append({
                    "template": agent_template,
                    "weight": scorecard_agent["weight"],
                    "configuration": scorecard_agent.get("configuration", {}),
                    "execution_order": scorecard_agent.get("executionOrder", 0),
                    "is_required": scorecard_agent["isRequired"]
                })
        
        # Sort by execution order
        required_agents.sort(key=lambda x: x["execution_order"])
        
        return required_agents
    
    def build_execution_plan(self, agents: List[dict]) -> dict:
        """Build execution plan based on agent dependencies and requirements"""
        
        # Separate agents by execution requirements
        parallel_agents = []
        sequential_agents = []
        
        for agent in agents:
            execution_order = agent.get("execution_order", 0)
            if execution_order == 0:
                parallel_agents.append(agent)
            else:
                sequential_agents.append(agent)
        
        return {
            "parallel_phase": parallel_agents,
            "sequential_phases": self._group_by_execution_order(sequential_agents),
            "total_agents": len(agents)
        }
    
    async def execute_agents(
        self, 
        execution_plan: dict, 
        interaction_data: dict,
        analysis_id: str,
        trace_id: str
    ) -> dict:
        """Execute agents according to the execution plan"""
        
        await self._update_session_phase(analysis_id, "agent_execution")
        
        agent_results = {}
        
        # Execute parallel agents first
        if execution_plan["parallel_phase"]:
            parallel_tasks = []
            for agent_config in execution_plan["parallel_phase"]:
                task = self._execute_single_agent(
                    agent_config, 
                    interaction_data, 
                    trace_id
                )
                parallel_tasks.append(task)
            
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            
            for i, result in enumerate(parallel_results):
                agent_name = execution_plan["parallel_phase"][i]["template"]["name"]
                if isinstance(result, Exception):
                    agent_results[agent_name] = {"error": str(result)}
                else:
                    agent_results[agent_name] = result
        
        # Execute sequential phases
        for phase_agents in execution_plan["sequential_phases"]:
            for agent_config in phase_agents:
                try:
                    result = await self._execute_single_agent(
                        agent_config, 
                        interaction_data, 
                        trace_id,
                        context=agent_results  # Pass previous results as context
                    )
                    agent_results[agent_config["template"]["name"]] = result
                except Exception as e:
                    agent_results[agent_config["template"]["name"]] = {"error": str(e)}
        
        return agent_results
    
    async def aggregate_results(
        self, 
        agent_results: dict, 
        scorecard: dict,
        analysis_id: str
    ) -> 'AnalysisResult':
        """Aggregate individual agent results into final analysis"""
        
        await self._update_session_phase(analysis_id, "result_aggregation")
        
        return await self.result_aggregator.aggregate(
            agent_results, 
            scorecard["aggregationRules"],
            scorecard["thresholds"]
        )
    
    async def _execute_single_agent(
        self, 
        agent_config: dict, 
        interaction_data: dict, 
        trace_id: str,
        context: dict = None
    ) -> dict:
        """Execute a single agent with timeout and error handling"""
        
        agent = await self.agent_factory.create_agent(agent_config["template"])
        
        # Prepare agent input
        agent_input = {
            "interaction": interaction_data,
            "configuration": agent_config.get("configuration", {}),
            "context": context or {},
            "trace_id": trace_id
        }
        
        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                agent.analyze(agent_input),
                timeout=30.0  # 30 second timeout per agent
            )
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Agent {agent_config['template']['name']} timed out")
    
    def _should_activate_agent(self, agent_template: dict, content_metadata: dict) -> bool:
        """Determine if an agent should be activated based on trigger rules"""
        
        trigger_rules = agent_template.get("triggerRules", {})
        
        # Check content type triggers
        content_types = trigger_rules.get("content_type", [])
        if content_types and content_metadata["interaction_type"] not in content_types:
            return False
        
        # Check topic triggers
        required_topics = trigger_rules.get("required_topics", [])
        if required_topics:
            detected_topics = content_metadata.get("detected_topics", [])
            if not any(topic in detected_topics for topic in required_topics):
                return False
        
        # Check regulatory indicators
        regulatory_reqs = trigger_rules.get("regulatory_indicators", [])
        if regulatory_reqs:
            detected_indicators = content_metadata.get("regulatory_indicators", [])
            if not any(indicator in detected_indicators for indicator in regulatory_reqs):
                return False
        
        return True
    
    def _group_by_execution_order(self, agents: List[dict]) -> List[List[dict]]:
        """Group agents by execution order for sequential processing"""
        
        groups = {}
        for agent in agents:
            order = agent.get("execution_order", 0)
            if order not in groups:
                groups[order] = []
            groups[order].append(agent)
        
        return [groups[order] for order in sorted(groups.keys())]
    
    async def _update_session_phase(self, analysis_id: str, phase: str):
        """Update the current phase in Redis session cache"""
        
        session_key = f"analysis:session:{analysis_id}"
        session_data = await self.cache.get(session_key)
        
        if session_data:
            session = json.loads(session_data)
            session["phase"] = phase
            await self.cache.setex(session_key, 1800, json.dumps(session))
```

### 2. Agent Factory Implementation

```python
# src/agents/factory.py
from google.adk.agents import Agent
from typing import Dict, Any
import json

class AgentFactory:
    """Factory for creating ADK agents from database templates"""
    
    def __init__(self):
        self.db = Prisma()
        self.cache = redis.Redis()
        self.model_registry = ModelRegistry()
        self.tool_registry = ToolRegistry()
    
    async def create_agent(self, template: dict) -> 'TahoeAgent':
        """Create an ADK agent from a template configuration"""
        
        # Get model configuration
        model_config = self.model_registry.get_config(
            template["model"],
            template.get("modelConfig", {})
        )
        
        # Load tools
        tools = await self.tool_registry.load_tools(template.get("tools", []))
        
        # Create base ADK agent
        adk_agent = Agent(
            name=template["name"],
            model=model_config.model_string,
            description=template.get("description", ""),
            tools=tools,
            **model_config.parameters
        )
        
        # Wrap in Tahoe agent for additional functionality
        return TahoeAgent(
            adk_agent=adk_agent,
            template=template,
            factory=self
        )
    
    async def load_template(self, template_id: str) -> dict:
        """Load agent template with caching"""
        
        # Check cache
        cached = await self.cache.get(f"agent:template:{template_id}")
        if cached:
            return json.loads(cached)
        
        # Load from database
        template = await self.db.agenttemplate.find_unique({
            "where": {"id": template_id}
        })
        
        if not template:
            raise ValueError(f"Agent template {template_id} not found")
        
        # Cache for reuse
        await self.cache.setex(
            f"agent:template:{template_id}",
            300,  # 5 minutes
            json.dumps(template, default=str)
        )
        
        return template

class TahoeAgent:
    """Wrapper around ADK agent with Tahoe-specific functionality"""
    
    def __init__(self, adk_agent: Agent, template: dict, factory: AgentFactory):
        self.adk_agent = adk_agent
        self.template = template
        self.factory = factory
        
    async def analyze(self, input_data: dict) -> dict:
        """Execute analysis with Tahoe-specific processing"""
        
        # Prepare prompts
        system_prompt = self.template.get("systemPrompt", "")
        user_prompt = self._build_user_prompt(input_data)
        
        # Execute ADK agent
        result = await self.adk_agent.run(
            input=user_prompt,
            system=system_prompt
        )
        
        # Process and structure result
        return self._process_result(result, input_data)
    
    def _build_user_prompt(self, input_data: dict) -> str:
        """Build user prompt from template and input data"""
        
        base_prompt = self.template.get("userPrompt", "")
        
        # Replace template variables
        prompt = base_prompt.format(
            interaction=input_data.get("interaction", {}),
            configuration=input_data.get("configuration", {}),
            context=input_data.get("context", {})
        )
        
        return prompt
    
    def _process_result(self, result: Any, input_data: dict) -> dict:
        """Process ADK agent result into standardized format"""
        
        return {
            "agent_name": self.template["name"],
            "agent_version": self.template["version"],
            "result": result,
            "confidence": self._calculate_confidence(result),
            "execution_time": getattr(result, 'execution_time', None),
            "model_used": self.template["model"],
            "trace_id": input_data.get("trace_id")
        }
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence score for the result"""
        # Implementation depends on result structure
        # This is a placeholder
        return 0.85
```

### 3. Model Registry

```python
# src/models/registry.py
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    model_string: str
    parameters: Dict[str, Any]
    provider: str

class ModelRegistry:
    """Manages multiple model providers and configurations"""
    
    PROVIDERS = {
        "gemini": {
            "models": {
                "gemini-2.0-flash": {
                    "string": "gemini-2.0-flash",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 0.95
                    }
                },
                "gemini-1.5-pro": {
                    "string": "gemini-1.5-pro",
                    "default_params": {
                        "temperature": 0.5,
                        "max_tokens": 4000,
                        "top_p": 0.95
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
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "gpt-4o": {
                    "string": "gpt-4o",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
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
                        "max_output_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "claude-3-sonnet": {
                    "string": "claude-3-sonnet-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_output_tokens": 2000,
                        "top_p": 1.0
                    }
                }
            }
        }
    }
    
    def get_config(self, model_name: str, overrides: Dict[str, Any] = None) -> ModelConfig:
        """Get model configuration with optional parameter overrides"""
        
        # Parse provider from model name
        provider = self._get_provider(model_name)
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider for model: {model_name}")
        
        if model_name not in self.PROVIDERS[provider]["models"]:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_config = self.PROVIDERS[provider]["models"][model_name]
        
        # Merge with overrides
        params = {**model_config["default_params"]}
        if overrides:
            params.update(overrides)
        
        return ModelConfig(
            model_string=model_config["string"],
            parameters=params,
            provider=provider
        )
    
    def _get_provider(self, model_name: str) -> str:
        """Determine provider from model name"""
        
        if model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        else:
            raise ValueError(f"Cannot determine provider for model: {model_name}")
    
    async def check_model_availability(self, model_name: str) -> bool:
        """Check if a model is currently available"""
        
        # This would implement actual availability checking
        # For now, return True for known models
        try:
            self.get_config(model_name)
            return True
        except ValueError:
            return False
```

---

## API Implementation (FastAPI)

### Main Application Structure

```python
# src/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
import logging

# Import internal modules
from .orchestrator import TahoeOrchestrator
from .auth import verify_service_token, AuthContext
from .models.api import *
from .services.monitoring import MetricsCollector
from .services.health import HealthChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="agent-engine",
    description="Multi-agent orchestration for compliance analysis",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize services
orchestrator = TahoeOrchestrator()
metrics = MetricsCollector()
health_checker = HealthChecker()

# Request/Response Models
class AnalysisRequest(BaseModel):
    interaction: InteractionData
    scorecard_id: str = Field(..., description="ID of the scorecard to use")
    portfolio_id: str = Field(..., description="Portfolio context ID")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    overall_score: Optional[float] = None
    confidence: Optional[float] = None
    categories: Optional[Dict[str, Any]] = None
    violations: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    audit_trail: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class InteractionData(BaseModel):
    id: str
    type: str  # "call", "email", "chat", etc.
    content: str  # transcript, email body, etc.
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Core Analysis Endpoints
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_interaction(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    auth: AuthContext = Depends(verify_service_token)
):
    """Submit interaction for multi-agent analysis"""
    
    try:
        # Start metrics tracking
        start_time = datetime.now()
        metrics.analysis_requests_total.inc()
        
        logger.info(f"Starting analysis for interaction {request.interaction.id}")
        
        # Execute analysis
        result = await orchestrator.analyze_interaction(
            request.interaction.dict(),
            request.scorecard_id,
            request.portfolio_id,
            request.options
        )
        
        # Track execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        metrics.analysis_duration_seconds.observe(execution_time)
        
        # Return structured response
        response = AnalysisResponse(
            analysis_id=result.analysis_id,
            status="complete",
            overall_score=result.overall_score,
            confidence=result.confidence,
            categories=result.categories,
            violations=result.violations,
            recommendations=result.recommendations,
            audit_trail=result.audit_trail,
            execution_time=execution_time
        )
        
        logger.info(f"Analysis completed for {request.interaction.id}: score={result.overall_score}")
        
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed for {request.interaction.id}: {str(e)}")
        metrics.analysis_errors_total.inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    auth: AuthContext = Depends(verify_service_token)
):
    """Retrieve analysis results by ID"""
    
    try:
        db = Prisma()
        analysis = await db.analysis.find_unique({
            "where": {"id": analysis_id}
        })
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisResponse(
            analysis_id=analysis.id,
            status=analysis.status,
            overall_score=analysis.overallScore,
            confidence=analysis.confidence,
            categories=analysis.results.get("categories", {}) if analysis.results else {},
            violations=analysis.violations or [],
            recommendations=analysis.recommendations or [],
            audit_trail={
                "trace_id": analysis.traceId,
                "execution_time": analysis.executionTime,
                "created_at": analysis.createdAt.isoformat(),
                "completed_at": analysis.completedAt.isoformat() if analysis.completedAt else None
            },
            execution_time=analysis.executionTime
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Management Endpoints
@app.post("/agents/templates")
async def create_agent_template(
    template: AgentTemplateCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new agent template"""
    
    try:
        db = Prisma()
        agent = await db.agenttemplate.create({
            "data": template.dict()
        })
        
        logger.info(f"Created agent template: {agent.name}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create agent template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/agents/templates/{template_id}")
async def update_agent_template(
    template_id: str,
    updates: AgentTemplateUpdate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Update agent template"""
    
    try:
        db = Prisma()
        cache = redis.Redis()
        
        # Get current version
        current = await db.agenttemplate.find_unique({
            "where": {"id": template_id}
        })
        
        if not current:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Update with version increment
        agent = await db.agenttemplate.update({
            "where": {"id": template_id},
            "data": {
                **updates.dict(exclude_unset=True),
                "version": current.version + 1,
                "updatedAt": datetime.now()
            }
        })
        
        # Invalidate cache
        await cache.delete(f"agent:template:{template_id}")
        
        logger.info(f"Updated agent template {template_id} to version {agent.version}")
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent template {template_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/templates")
async def list_agent_templates(
    active_only: bool = True,
    auth: AuthContext = Depends(verify_service_token)
):
    """List available agent templates"""
    
    try:
        db = Prisma()
        
        where_clause = {"isActive": True} if active_only else {}
        
        templates = await db.agenttemplate.find_many({
            "where": where_clause,
            "order_by": {"name": "asc"}
        })
        
        return templates
        
    except Exception as e:
        logger.error(f"Failed to list agent templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scorecards")
async def create_scorecard(
    scorecard: ScorecardCreate,
    auth: AuthContext = Depends(verify_service_token)
):
    """Create new scorecard configuration"""
    
    try:
        db = Prisma()
        result = await db.scorecard.create({
            "data": scorecard.dict()
        })
        
        logger.info(f"Created scorecard: {result.name}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to create scorecard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scorecards")
async def list_scorecards(
    portfolio_id: Optional[str] = None,
    active_only: bool = True,
    auth: AuthContext = Depends(verify_service_token)
):
    """List available scorecards"""
    
    try:
        db = Prisma()
        
        where_clause = {}
        if portfolio_id:
            where_clause["portfolioId"] = portfolio_id
        if active_only:
            where_clause["isActive"] = True
        
        scorecards = await db.scorecard.find_many({
            "where": where_clause,
            "include": {
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            },
            "order_by": {"name": "asc"}
        })
        
        return scorecards
        
    except Exception as e:
        logger.error(f"Failed to list scorecards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health and Monitoring Endpoints
@app.get("/health")
async def health_check():
    """Service health check"""
    
    health_status = await health_checker.check_all()
    
    if health_status["overall_status"] == "healthy":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

@app.get("/metrics")
async def get_metrics():
    """Service operational metrics"""
    
    try:
        return await metrics.get_current_metrics()
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/analysis/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    auth: AuthContext = Depends(verify_service_token)
):
    """Get real-time analysis status"""
    
    try:
        cache = redis.Redis()
        
        # Check session cache first
        session_data = await cache.get(f"analysis:session:{analysis_id}")
        if session_data:
            session = json.loads(session_data)
            return {
                "analysis_id": analysis_id,
                "status": session.get("status", "unknown"),
                "phase": session.get("phase", "unknown"),
                "started_at": session.get("started_at"),
                "trace_id": session.get("trace_id")
            }
        
        # Fallback to database
        db = Prisma()
        analysis = await db.analysis.find_unique({
            "where": {"id": analysis_id},
            "select": {
                "id": True,
                "status": True,
                "createdAt": True,
                "completedAt": True,
                "traceId": True
            }
        })
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis_id": analysis.id,
            "status": analysis.status,
            "created_at": analysis.createdAt.isoformat(),
            "completed_at": analysis.completedAt.isoformat() if analysis.completedAt else None,
            "trace_id": analysis.traceId
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup/Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    
    logger.info("Starting agent-engine service")
    
    # Initialize database connection
    await orchestrator.db.connect()
    
    # Initialize Redis connection
    await orchestrator.cache.ping()
    
    # Warm up caches
    await warmup_caches()
    
    logger.info("agent-engine service started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    
    logger.info("Shutting down agent-engine service")
    
    # Close database connection
    await orchestrator.db.disconnect()
    
    logger.info("agent-engine service shutdown complete")

async def warmup_caches():
    """Pre-populate frequently used cache entries"""
    
    try:
        # Load active agent templates
        templates = await orchestrator.db.agenttemplate.find_many({
            "where": {"isActive": True}
        })
        
        for template in templates:
            await orchestrator.cache.setex(
                f"agent:template:{template.id}",
                300,
                json.dumps(template, default=str)
            )
        
        logger.info(f"Warmed up cache with {len(templates)} agent templates")
        
    except Exception as e:
        logger.warning(f"Cache warmup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Configuration Management

### Environment Configuration

```python
# src/config.py
from pydantic import BaseSettings
from typing import Optional

class ServiceConfig(BaseSettings):
    # Service Identity
    SERVICE_NAME: str = "agent-engine"
    SERVICE_TOKEN: str  # Internal auth token
    SERVICE_VERSION: str = "1.0.0"
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 100
    
    # Model Provider API Keys
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Performance Tuning
    MAX_CONCURRENT_ANALYSES: int = 100
    AGENT_TIMEOUT_SECONDS: int = 30
    ANALYSIS_TIMEOUT_SECONDS: int = 300
    CACHE_TTL_AGENT_TEMPLATE: int = 300  # 5 minutes
    CACHE_TTL_SCORECARD: int = 300       # 5 minutes
    CACHE_TTL_PORTFOLIO: int = 600       # 10 minutes
    
    # Security
    CORS_ORIGINS: list = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Observability
    LOG_LEVEL: str = "INFO"
    TRACE_ENABLED: bool = True
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Feature Flags
    ENABLE_PARALLEL_EXECUTION: bool = True
    ENABLE_RESULT_CACHING: bool = True
    ENABLE_AGENT_PERFORMANCE_TRACKING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global configuration instance
config = ServiceConfig()
```

### Dynamic Configuration Manager

```python
# src/services/configuration.py
import json
from typing import Dict, Any
from prisma import Prisma
import redis.asyncio as redis

class ConfigurationManager:
    """Manages runtime configuration updates and hot reloading"""
    
    def __init__(self):
        self.db = Prisma()
        self.cache = redis.Redis()
        self.subscribers = []
    
    async def update_scorecard(self, scorecard_id: str, updates: Dict[str, Any]):
        """Update scorecard configuration with cache invalidation"""
        
        # Update in database
        scorecard = await self.db.scorecard.update({
            "where": {"id": scorecard_id},
            "data": {
                **updates,
                "version": {"increment": 1},
                "updatedAt": datetime.now()
            }
        })
        
        # Invalidate cache
        await self.cache.delete(f"scorecard:{scorecard_id}")
        
        # Notify subscribers of configuration change
        await self._notify_config_change("scorecard", scorecard_id, updates)
        
        return scorecard
    
    async def toggle_agent(self, agent_id: str, active: bool):
        """Enable/disable an agent template"""
        
        agent = await self.db.agenttemplate.update({
            "where": {"id": agent_id},
            "data": {
                "isActive": active,
                "updatedAt": datetime.now()
            }
        })
        
        # Clear agent cache
        await self.cache.delete(f"agent:template:{agent_id}")
        
        await self._notify_config_change("agent", agent_id, {"active": active})
        
        return agent
    
    async def update_agent_template(self, agent_id: str, updates: Dict[str, Any]):
        """Update agent template with versioning"""
        
        agent = await self.db.agenttemplate.update({
            "where": {"id": agent_id},
            "data": {
                **updates,
                "version": {"increment": 1},
                "updatedAt": datetime.now()
            }
        })
        
        # Invalidate cache
        await self.cache.delete(f"agent:template:{agent_id}")
        
        await self._notify_config_change("agent", agent_id, updates)
        
        return agent
    
    async def get_portfolio_configuration(self, portfolio_id: str) -> Dict[str, Any]:
        """Get portfolio-specific configuration with caching"""
        
        # Try cache first
        cached = await self.cache.get(f"portfolio:{portfolio_id}")
        if cached:
            return json.loads(cached)
        
        # Load from database
        portfolio = await self.db.portfolio.find_unique({
            "where": {"id": portfolio_id},
            "include": {
                "scorecards": {
                    "where": {"isActive": True},
                    "include": {
                        "scorecardAgents": {
                            "include": {"agent": True}
                        }
                    }
                }
            }
        })
        
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        # Cache the result
        await self.cache.setex(
            f"portfolio:{portfolio_id}",
            config.CACHE_TTL_PORTFOLIO,
            json.dumps(portfolio, default=str)
        )
        
        return portfolio
    
    async def _notify_config_change(self, entity_type: str, entity_id: str, changes: Dict[str, Any]):
        """Notify subscribers of configuration changes"""
        
        notification = {
            "type": "config_change",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changes": changes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publish to Redis pub/sub for distributed notifications
        await self.cache.publish("config_changes", json.dumps(notification))
        
        # Notify local subscribers
        for subscriber in self.subscribers:
            try:
                await subscriber(notification)
            except Exception as e:
                logger.warning(f"Failed to notify subscriber: {str(e)}")
    
    def subscribe_to_changes(self, callback):
        """Subscribe to configuration changes"""
        self.subscribers.append(callback)
```

---

## Deployment and Operations

### Project Structure

```
agent-engine/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── orchestrator.py            # Core orchestration engine
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── factory.py             # Agent factory
│   │   ├── base.py                # Base agent classes
│   │   └── specialists/           # Specialist agent implementations
│   │       ├── compliance.py      # Compliance specialist
│   │       ├── quality.py         # Quality assessment specialist
│   │       ├── identity.py        # Identity verification specialist
│   │       └── risk.py            # Risk evaluation specialist
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py            # Prisma database models
│   │   ├── api.py                 # Pydantic API models
│   │   ├── registry.py            # Model provider registry
│   │   └── cache.py               # Cache data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis.py            # Analysis services
│   │   ├── configuration.py       # Configuration management
│   │   ├── aggregation.py         # Result aggregation
│   │   ├── monitoring.py          # Metrics and monitoring
│   │   └── health.py              # Health check services
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py            # Tool registry
│   │   ├── regulatory.py          # Regulatory database tools
│   │   └── validation.py          # Validation tools
│   └── utils/
│       ├── __init__.py
│       ├── auth.py                # Authentication utilities
│       ├── tracing.py             # Distributed tracing
│       ├── errors.py              # Error handling
│       └── formatting.py          # Response formatting
├── prisma/
│   ├── schema.prisma              # Database schema
│   └── migrations/                # Database migrations
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   ├── fixtures/                  # Test fixtures
│   └── conftest.py                # Pytest configuration
├── docs/
│   ├── api.md                     # API documentation
│   ├── deployment.md              # Deployment guide
│   └── architecture.md            # Architecture documentation
├── scripts/
│   ├── setup.py                   # Setup script
│   ├── seed.py                    # Database seeding
│   └── migrate.py                 # Migration scripts
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Local development environment
├── .env.example                   # Environment variable template
├── pyproject.toml                 # Python project configuration
└── README.md                      # Project documentation
```

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY prisma/ ./prisma/
COPY scripts/ ./scripts/

# Generate Prisma client
RUN python -m prisma generate

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Runtime configuration
ENV SERVICE_NAME=agent-engine
ENV PORT=8000
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent-engine:
    build: .
    container_name: agent-engine
    environment:
      - SERVICE_TOKEN=${SERVICE_TOKEN}
      - DATABASE_URL=postgresql://tahoe:tahoe@postgres:5432/tahoe
      - REDIS_URL=redis://redis:6379
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./src:/app/src  # For development hot reload
    networks:
      - tahoe-network
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: tahoe-postgres
    environment:
      - POSTGRES_USER=tahoe
      - POSTGRES_PASSWORD=tahoe
      - POSTGRES_DB=tahoe
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - tahoe-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tahoe"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: tahoe-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - tahoe-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Optional: Redis Commander for debugging
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: redis-commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    networks:
      - tahoe-network

volumes:
  postgres_data:
  redis_data:

networks:
  tahoe-network:
    driver: bridge
```

### Requirements Files

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
prisma==0.11.0
redis[hiredis]==5.0.1
google-adk[full]==0.1.0
httpx==0.25.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
structlog==23.2.0
```

```txt
# requirements-dev.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
```

---

## Development Workflow Commands

### Essential Commands for Claude Code

```bash
# Development setup
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Database operations
python -m prisma db push              # Push schema changes
python -m prisma generate            # Generate client
python -m prisma migrate dev         # Create and apply migration
python scripts/seed.py               # Seed with initial data

# Development server
uvicorn src.main:app --reload --port 8000

# Testing
pytest tests/ -v                     # Run all tests
pytest tests/unit/ -v                # Unit tests only
pytest tests/integration/ -v         # Integration tests only
pytest --cov=src tests/              # Coverage report

# Code formatting
black src/ tests/                    # Format code
isort src/ tests/                    # Sort imports
flake8 src/ tests/                   # Lint code
mypy src/                            # Type checking

# Docker operations
docker-compose up -d                 # Start all services
docker-compose logs agent-engine    # View logs
docker-compose exec agent-engine bash # Shell into container
docker-compose down                  # Stop all services

# Database management
docker-compose exec postgres psql -U tahoe -d tahoe  # Connect to DB
docker-compose exec redis redis-cli  # Connect to Redis

# Monitoring
curl http://localhost:8000/health    # Health check
curl http://localhost:8000/metrics   # Service metrics
```

### Common Development Tasks

```bash
# Add new agent template
curl -X POST http://localhost:8000/agents/templates \
  -H "Authorization: Bearer ${SERVICE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new_specialist",
    "type": "specialist",
    "model": "gemini-2.0-flash",
    "capabilities": ["new_capability"],
    "tools": ["custom_tool"]
  }'

# Test analysis endpoint
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer ${SERVICE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "interaction": {
      "id": "test_001",
      "type": "call",
      "content": "Test transcript content",
      "metadata": {"duration": 300}
    },
    "scorecard_id": "test_scorecard",
    "portfolio_id": "test_portfolio"
  }'

# Monitor analysis progress
curl http://localhost:8000/status/analysis/{analysis_id} \
  -H "Authorization: Bearer ${SERVICE_TOKEN}"

# Get analysis results
curl http://localhost:8000/analysis/{analysis_id} \
  -H "Authorization: Bearer ${SERVICE_TOKEN}"
```

---

## Specialist Agent Implementations

### Base Agent Interface

```python
# src/agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass
import time

@dataclass
class AgentResult:
    """Standardized agent result format"""
    agent_name: str
    agent_version: str
    score: float  # 0-100
    confidence: float  # 0-1
    findings: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    execution_time: float
    metadata: Dict[str, Any]

class BaseSpecialistAgent(ABC):
    """Base class for all specialist agents"""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        
    @abstractmethod
    async def analyze(self, interaction: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """Perform specialized analysis on the interaction"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides"""
        pass
    
    def _measure_execution_time(self, func):
        """Decorator to measure execution time"""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            if hasattr(result, 'execution_time'):
                result.execution_time = execution_time
            return result
        return wrapper
```

### Compliance Specialist Agent

```python
# src/agents/specialists/compliance.py
from google.adk.agents import Agent
from google.adk.tools import tool
from ..base import BaseSpecialistAgent, AgentResult
import re
from typing import Dict, Any, List

class ComplianceSpecialistAgent(BaseSpecialistAgent):
    """Specialist agent for regulatory compliance analysis"""
    
    def __init__(self):
        super().__init__("compliance_analyst", "1.0")
        self.regulations = {
            "fdcpa": self._load_fdcpa_rules(),
            "reg_f": self._load_reg_f_rules(),
            "tcpa": self._load_tcpa_rules()
        }
    
    async def analyze(self, interaction: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """Analyze interaction for compliance violations"""
        
        start_time = time.time()
        
        # Extract transcript content
        content = interaction.get("content", "")
        interaction_type = interaction.get("type", "unknown")
        
        # Initialize analysis results
        findings = []
        violations = []
        recommendations = []
        
        # Analyze for each relevant regulation
        if self._is_debt_collection_context(content):
            fdcpa_analysis = await self._analyze_fdcpa_compliance(content, interaction)
            findings.extend(fdcpa_analysis["findings"])
            violations.extend(fdcpa_analysis["violations"])
            recommendations.extend(fdcpa_analysis["recommendations"])
        
        if interaction_type == "call":
            tcpa_analysis = await self._analyze_tcpa_compliance(content, interaction)
            findings.extend(tcpa_analysis["findings"])
            violations.extend(tcpa_analysis["violations"])
            recommendations.extend(tcpa_analysis["recommendations"])
        
        # Calculate overall compliance score
        score = self._calculate_compliance_score(violations, findings)
        confidence = self._calculate_confidence(findings)
        
        execution_time = time.time() - start_time
        
        return AgentResult(
            agent_name=self.name,
            agent_version=self.version,
            score=score,
            confidence=confidence,
            findings=findings,
            violations=violations,
            recommendations=recommendations,
            execution_time=execution_time,
            metadata={
                "regulations_checked": list(self.regulations.keys()),
                "interaction_type": interaction_type
            }
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "fdcpa_compliance",
            "reg_f_validation", 
            "tcpa_compliance",
            "regulatory_violation_detection"
        ]
    
    async def _analyze_fdcpa_compliance(self, content: str, interaction: Dict[str, Any]) -> Dict[str, List]:
        """Analyze for FDCPA (Fair Debt Collection Practices Act) compliance"""
        
        findings = []
        violations = []
        recommendations = []
        
        # Check for required disclosures
        if not self._has_required_disclosure(content):
            violations.append({
                "type": "missing_disclosure",
                "regulation": "FDCPA",
                "section": "15 USC 1692e",
                "description": "Required debt collection disclosure not found",
                "severity": "high",
                "evidence": self._extract_evidence(content, "disclosure")
            })
            recommendations.append({
                "type": "add_disclosure",
                "description": "Include required FDCPA disclosure at beginning of call",
                "priority": "high"
            })
        
        # Check for prohibited threats
        threats = self._detect_prohibited_threats(content)
        for threat in threats:
            violations.append({
                "type": "prohibited_threat",
                "regulation": "FDCPA",
                "section": "15 USC 1692e(5)",
                "description": f"Prohibited threat detected: {threat['type']}",
                "severity": "critical",
                "evidence": threat["text"]
            })
        
        # Check for harassment indicators
        harassment = self._detect_harassment_patterns(content)
        if harassment:
            violations.append({
                "type": "harassment",
                "regulation": "FDCPA", 
                "section": "15 USC 1692d",
                "description": "Potential harassment behavior detected",
                "severity": "high",
                "evidence": harassment
            })
        
        # Check validation requirements
        if self._requires_debt_validation(content) and not self._has_validation_notice(content):
            violations.append({
                "type": "missing_validation_notice",
                "regulation": "FDCPA",
                "section": "15 USC 1692g",
                "description": "Debt validation notice required but not provided",
                "severity": "medium",
                "evidence": "Consumer requested validation information"
            })
        
        return {
            "findings": findings,
            "violations": violations,
            "recommendations": recommendations
        }
    
    async def _analyze_tcpa_compliance(self, content: str, interaction: Dict[str, Any]) -> Dict[str, List]:
        """Analyze for TCPA (Telephone Consumer Protection Act) compliance"""
        
        findings = []
        violations = []
        recommendations = []
        
        # Check for consent verification (for calls to cell phones)
        metadata = interaction.get("metadata", {})
        if metadata.get("phone_type") == "mobile":
            if not self._has_consent_verification(content):
                violations.append({
                    "type": "missing_consent",
                    "regulation": "TCPA",
                    "section": "47 USC 227",
                    "description": "No consent verification for mobile phone call",
                    "severity": "high",
                    "evidence": "Call made to mobile number without consent verification"
                })
        
        # Check for opt-out compliance
        if self._contains_opt_out_request(content) and not self._acknowledges_opt_out(content):
            violations.append({
                "type": "ignored_opt_out",
                "regulation": "TCPA",
                "section": "47 USC 227",
                "description": "Consumer opt-out request not properly acknowledged",
                "severity": "critical",
                "evidence": self._extract_opt_out_request(content)
            })
        
        return {
            "findings": findings,
            "violations": violations,
            "recommendations": recommendations
        }
    
    def _is_debt_collection_context(self, content: str) -> bool:
        """Determine if this is a debt collection interaction"""
        debt_indicators = [
            "payment", "debt", "owe", "collection", "balance",
            "past due", "overdue", "settlement", "payment plan"
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in debt_indicators)
    
    def _has_required_disclosure(self, content: str) -> bool:
        """Check if required FDCPA disclosure is present"""
        disclosure_patterns = [
            r"this is an attempt to collect a debt",
            r"this communication is from a debt collector",
            r"any information obtained will be used for that purpose"
        ]
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in disclosure_patterns)
    
    def _detect_prohibited_threats(self, content: str) -> List[Dict[str, str]]:
        """Detect prohibited threats or false statements"""
        threats = []
        
        threat_patterns = [
            (r"arrest|jail|prison", "arrest_threat"),
            (r"garnish.*wage|seize.*property", "property_threat"),
            (r"sue|lawsuit|legal action", "legal_threat"),
            (r"ruin.*credit|destroy.*credit", "credit_threat")
        ]
        
        for pattern, threat_type in threat_patterns:
            matches = re.finditer(pattern, content.lower())
            for match in matches:
                threats.append({
                    "type": threat_type,
                    "text": match.group(0),
                    "context": content[max(0, match.start()-50):match.end()+50]
                })
        
        return threats
    
    def _detect_harassment_patterns(self, content: str) -> List[str]:
        """Detect patterns that might constitute harassment"""
        harassment_indicators = []
        
        # Check for excessive frequency language
        if re.search(r"call.*multiple times|call.*repeatedly", content.lower()):
            harassment_indicators.append("Mentions of repeated calling")
        
        # Check for abusive language
        profanity_pattern = r'\b(damn|hell|stupid|idiot)\b'
        if re.search(profanity_pattern, content.lower()):
            harassment_indicators.append("Use of potentially abusive language")
        
        # Check for threatening tone
        if re.search(r"you better|you have to|you must", content.lower()):
            harassment_indicators.append("Demanding or threatening language")
        
        return harassment_indicators
    
    def _requires_debt_validation(self, content: str) -> bool:
        """Check if debt validation was requested"""
        validation_requests = [
            "validate", "verification", "prove", "documentation",
            "evidence of debt", "show me proof"
        ]
        content_lower = content.lower()
        return any(request in content_lower for request in validation_requests)
    
    def _has_validation_notice(self, content: str) -> bool:
        """Check if debt validation notice was provided"""
        validation_language = [
            "validation notice", "dispute this debt", "request validation",
            "verification of debt", "written notice"
        ]
        content_lower = content.lower()
        return any(language in content_lower for language in validation_language)
    
    def _has_consent_verification(self, content: str) -> bool:
        """Check if consent for mobile calls was verified"""
        consent_patterns = [
            "consent to call", "permission to contact", "agreed to receive calls",
            "authorized contact", "consent on file"
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in consent_patterns)
    
    def _contains_opt_out_request(self, content: str) -> bool:
        """Check if consumer requested to opt out"""
        opt_out_patterns = [
            "stop calling", "don't call", "remove.*number", "opt out",
            "take me off", "no more calls", "stop contacting"
        ]
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in opt_out_patterns)
    
    def _acknowledges_opt_out(self, content: str) -> bool:
        """Check if opt-out request was acknowledged"""
        acknowledgment_patterns = [
            "remove.*number", "stop calling", "noted", "understand",
            "will not call", "remove from list"
        ]
        content_lower = content.lower()
        return any(pattern in content_lower for pattern in acknowledgment_patterns)
    
    def _extract_opt_out_request(self, content: str) -> str:
        """Extract the specific opt-out request for evidence"""
        opt_out_patterns = [
            r"[^.]*(?:stop calling|don't call|remove.*number|opt out)[^.]*",
            r"[^.]*(?:take me off|no more calls|stop contacting)[^.]*"
        ]
        
        for pattern in opt_out_patterns:
            match = re.search(pattern, content.lower())
            if match:
                return match.group(0)
        
        return "Opt-out request detected but exact text not captured"
    
    def _extract_evidence(self, content: str, evidence_type: str) -> str:
        """Extract relevant evidence from content"""
        # This would implement more sophisticated evidence extraction
        return f"Evidence extraction for {evidence_type} from content"
    
    def _calculate_compliance_score(self, violations: List[Dict], findings: List[Dict]) -> float:
        """Calculate overall compliance score based on violations"""
        if not violations:
            return 100.0
        
        # Weight violations by severity
        severity_weights = {"critical": 30, "high": 20, "medium": 10, "low": 5}
        total_deduction = sum(severity_weights.get(v.get("severity", "low"), 5) for v in violations)
        
        # Cap minimum score at 0
        score = max(0.0, 100.0 - total_deduction)
        return score
    
    def _calculate_confidence(self, findings: List[Dict]) -> float:
        """Calculate confidence in the analysis"""
        # Base confidence on number of checks performed and clarity of results
        base_confidence = 0.85
        
        # Adjust based on findings quality
        if len(findings) > 5:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _load_fdcpa_rules(self) -> Dict[str, Any]:
        """Load FDCPA regulatory rules"""
        return {
            "required_disclosures": [
                "This is an attempt to collect a debt",
                "Any information obtained will be used for that purpose"
            ],
            "prohibited_practices": [
                "Threats of arrest or legal action without intent",
                "Harassment or abuse",
                "False or misleading representations",
                "Unfair practices"
            ]
        }
    
    def _load_reg_f_rules(self) -> Dict[str, Any]:
        """Load Regulation F rules"""
        return {
            "call_frequency_limits": {
                "max_per_week": 7,
                "max_consecutive_days": 7
            },
            "time_restrictions": {
                "earliest": "08:00",
                "latest": "21:00",
                "timezone": "consumer_local"
            }
        }
    
    def _load_tcpa_rules(self) -> Dict[str, Any]:
        """Load TCPA rules"""
        return {
            "consent_requirements": {
                "mobile_calls": "express_written_consent",
                "robocalls": "prior_express_written_consent"
            },
            "opt_out_requirements": {
                "immediate_effect": True,
                "written_confirmation": True
            }
        }
```

### Quality Assessment Specialist Agent

```python
# src/agents/specialists/quality.py
from ..base import BaseSpecialistAgent, AgentResult
import re
from typing import Dict, Any, List
import asyncio

class QualityAssessmentAgent(BaseSpecialistAgent):
    """Specialist agent for interaction quality assessment"""
    
    def __init__(self):
        super().__init__("quality_assessor", "1.0")
        self.quality_metrics = [
            "professionalism", "clarity", "empathy", "effectiveness",
            "courtesy", "listening_skills", "problem_resolution"
        ]
    
    async def analyze(self, interaction: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """Analyze interaction quality across multiple dimensions"""
        
        start_time = time.time()
        
        content = interaction.get("content", "")
        metadata = interaction.get("metadata", {})
        
        # Perform parallel quality assessments
        assessments = await asyncio.gather(
            self._assess_professionalism(content),
            self._assess_clarity(content),
            self._assess_empathy(content),
            self._assess_effectiveness(content, metadata),
            self._assess_courtesy(content),
            self._assess_listening_skills(content),
            self._assess_problem_resolution(content)
        )
        
        # Combine assessments
        findings = []
        violations = []
        recommendations = []
        
        metric_scores = {}
        for i, metric in enumerate(self.quality_metrics):
            assessment = assessments[i]
            metric_scores[metric] = assessment["score"]
            findings.extend(assessment["findings"])
            if assessment["score"] < 60:  # Below acceptable threshold
                violations.extend(assessment["issues"])
            recommendations.extend(assessment["recommendations"])
        
        # Calculate overall quality score
        overall_score = sum(metric_scores.values()) / len(metric_scores)
        confidence = self._calculate_confidence(findings, metric_scores)
        
        execution_time = time.time() - start_time
        
        return AgentResult(
            agent_name=self.name,
            agent_version=self.version,
            score=overall_score,
            confidence=confidence,
            findings=findings,
            violations=violations,
            recommendations=recommendations,
            execution_time=execution_time,
            metadata={
                "metric_scores": metric_scores,
                "assessment_categories": self.quality_metrics
            }
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "quality_assessment",
            "professionalism_scoring",
            "communication_effectiveness",
            "customer_service_evaluation"
        ]
    
    async def _assess_professionalism(self, content: str) -> Dict[str, Any]:
        """Assess professionalism in communication"""
        
        findings = []
        issues = []
        recommendations = []
        score = 85  # Start with base score
        
        # Check for unprofessional language
        unprofessional_patterns = [
            r'\b(yeah|yep|nah|gonna|wanna|gotta)\b',
            r'\b(uh|um|er|ah)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[A-Z]{3,}'  # Excessive capitalization
        ]
        
        for pattern in unprofessional_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                score -= len(matches) * 5
                issues.append({
                    "type": "unprofessional_language",
                    "description": f"Unprofessional language detected: {pattern}",
                    "count": len(matches),
                    "severity": "medium"
                })
        
        # Check for professional greeting
        if not re.search(r'(good morning|good afternoon|hello|thank you for)', content.lower()):
            score -= 10
            recommendations.append({
                "type": "add_professional_greeting",
                "description": "Consider starting with a professional greeting"
            })
        
        # Check for proper closure
        if not re.search(r'(thank you|have a.*day|goodbye|take care)', content.lower()):
            score -= 5
            recommendations.append({
                "type": "add_professional_closure",
                "description": "End interaction with professional closure"
            })
        
        findings.append({
            "metric": "professionalism",
            "score": max(0, score),
            "details": "Assessment of professional language and tone"
        })
        
        return {
            "score": max(0, score),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_clarity(self, content: str) -> Dict[str, Any]:
        """Assess clarity and comprehensibility"""
        
        findings = []
        issues = []
        recommendations = []
        score = 80
        
        # Check sentence length (overly long sentences reduce clarity)
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            score -= len(long_sentences) * 5
            issues.append({
                "type": "overly_long_sentences",
                "description": f"{len(long_sentences)} sentences may be too long for clarity",
                "severity": "low"
            })
        
        # Check for jargon or complex terms
        jargon_terms = [
            'pursuant', 'heretofore', 'aforementioned', 'subsequently',
            'facilitate', 'utilize', 'aforementioned'
        ]
        
        jargon_found = []
        for term in jargon_terms:
            if re.search(rf'\b{term}\b', content, re.IGNORECASE):
                jargon_found.append(term)
        
        if jargon_found:
            score -= len(jargon_found) * 3
            recommendations.append({
                "type": "simplify_language",
                "description": f"Consider simplifying terms: {', '.join(jargon_found)}"
            })
        
        # Check for clear structure
        if not re.search(r'(first|second|next|then|finally)', content.lower()):
            score -= 5
            recommendations.append({
                "type": "improve_structure",
                "description": "Use transitional words to improve clarity"
            })
        
        findings.append({
            "metric": "clarity",
            "score": max(0, score),
            "details": "Assessment of communication clarity and structure"
        })
        
        return {
            "score": max(0, score),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_empathy(self, content: str) -> Dict[str, Any]:
        """Assess empathy and emotional intelligence"""
        
        findings = []
        issues = []
        recommendations = []
        score = 70  # Start lower as empathy requires active demonstration
        
        # Look for empathetic language
        empathy_indicators = [
            r'(understand|realize|appreciate)',
            r'(difficult|challenging|frustrating)',
            r'(sorry|apologize)',
            r'(help|assist|support)',
            r'(concern|worry|stress)'
        ]
        
        empathy_count = 0
        for pattern in empathy_indicators:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            empathy_count += matches
        
        score += min(empathy_count * 5, 30)  # Cap bonus at 30 points
        
        # Check for dismissive language
        dismissive_patterns = [
            r'(just|simply|only|merely)',
            r'(should have|could have)',
            r'(not my problem|not our fault)'
        ]
        
        for pattern in dismissive_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches:
                score -= matches * 8
                issues.append({
                    "type": "dismissive_language",
                    "description": f"Potentially dismissive language detected",
                    "pattern": pattern,
                    "severity": "medium"
                })
        
        if empathy_count < 2:
            recommendations.append({
                "type": "increase_empathy",
                "description": "Consider using more empathetic language to acknowledge customer concerns"
            })
        
        findings.append({
            "metric": "empathy",
            "score": max(0, min(100, score)),
            "details": f"Empathy indicators found: {empathy_count}"
        })
        
        return {
            "score": max(0, min(100, score)),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_effectiveness(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess interaction effectiveness and goal achievement"""
        
        findings = []
        issues = []
        recommendations = []
        score = 75
        
        # Check for clear call-to-action
        action_patterns = [
            r'(please|can you|would you)',
            r'(next step|following step)',
            r'(need to|should|will)'
        ]
        
        action_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in action_patterns)
        
        if action_count == 0:
            score -= 20
            issues.append({
                "type": "no_clear_action",
                "description": "No clear next steps or actions identified",
                "severity": "high"
            })
        
        # Check for information gathering
        question_count = len(re.findall(r'\?', content))
        if question_count < 2:
            score -= 10
            recommendations.append({
                "type": "gather_more_information",
                "description": "Ask more questions to better understand customer needs"
            })
        
        # Check for resolution attempt
        resolution_patterns = [
            r'(resolve|solution|fix|address)',
            r'(option|alternative|choice)',
            r'(payment plan|arrangement)'
        ]
        
        resolution_indicators = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in resolution_patterns)
        
        if resolution_indicators == 0:
            score -= 15
            issues.append({
                "type": "no_resolution_attempt",
                "description": "No clear resolution or options offered",
                "severity": "medium"
            })
        
        findings.append({
            "metric": "effectiveness",
            "score": max(0, score),
            "details": f"Actions: {action_count}, Questions: {question_count}, Resolution attempts: {resolution_indicators}"
        })
        
        return {
            "score": max(0, score),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_courtesy(self, content: str) -> Dict[str, Any]:
        """Assess courtesy and politeness"""
        
        findings = []
        issues = []
        recommendations = []
        score = 80
        
        # Look for polite language
        courtesy_indicators = [
            r'(please|thank you|thanks)',
            r'(excuse me|pardon)',
            r'(may I|could I|would it be possible)',
            r'(appreciate|grateful)'
        ]
        
        courtesy_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in courtesy_indicators)
        score += min(courtesy_count * 3, 20)
        
        # Check for impolite language
        impolite_patterns = [
            r'(shut up|be quiet)',
            r'(wrong|stupid|ridiculous)',
            r'(whatever|fine|sure)',
            r'(obviously|clearly|duh)'
        ]
        
        for pattern in impolite_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches:
                score -= matches * 15
                issues.append({
                    "type": "impolite_language",
                    "description": f"Potentially impolite language detected",
                    "severity": "high"
                })
        
        if courtesy_count < 3:
            recommendations.append({
                "type": "increase_courtesy",
                "description": "Use more courteous language (please, thank you, etc.)"
            })
        
        findings.append({
            "metric": "courtesy",
            "score": max(0, min(100, score)),
            "details": f"Courtesy indicators: {courtesy_count}"
        })
        
        return {
            "score": max(0, min(100, score)),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_listening_skills(self, content: str) -> Dict[str, Any]:
        """Assess active listening and responsiveness"""
        
        findings = []
        issues = []
        recommendations = []
        score = 75
        
        # Look for acknowledgment phrases
        listening_indicators = [
            r'(I see|I understand|I hear)',
            r'(so you\'re saying|let me understand)',
            r'(correct me if|did I understand)',
            r'(sounds like|seems like)'
        ]
        
        listening_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in listening_indicators)
        score += min(listening_count * 8, 25)
        
        # Check for interruption indicators
        interruption_patterns = [
            r'(but|however|wait)',
            r'(let me stop you|hold on)',
            r'(that\'s not|no that\'s wrong)'
        ]
        
        interruption_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in interruption_patterns)
        score -= interruption_count * 5
        
        if listening_count < 2:
            recommendations.append({
                "type": "improve_listening",
                "description": "Use more acknowledgment phrases to demonstrate active listening"
            })
        
        findings.append({
            "metric": "listening_skills",
            "score": max(0, min(100, score)),
            "details": f"Listening indicators: {listening_count}, Interruptions: {interruption_count}"
        })
        
        return {
            "score": max(0, min(100, score)),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    async def _assess_problem_resolution(self, content: str) -> Dict[str, Any]:
        """Assess problem resolution approach"""
        
        findings = []
        issues = []
        recommendations = []
        score = 70
        
        # Look for problem-solving language
        resolution_indicators = [
            r'(let\'s work|work together|find a solution)',
            r'(option|alternative|choice)',
            r'(what if|how about|consider)',
            r'(payment plan|arrangement|settlement)'
        ]
        
        resolution_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in resolution_indicators)
        score += min(resolution_count * 10, 30)
        
        # Check for follow-up commitment
        follow_up_patterns = [
            r'(follow up|get back|contact you)',
            r'(within.*days|by.*date)',
            r'(call you back|email you)'
        ]
        
        follow_up_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in follow_up_patterns)
        if follow_up_count > 0:
            score += 10
        else:
            recommendations.append({
                "type": "commit_to_follow_up",
                "description": "Provide specific follow-up commitments when appropriate"
            })
        
        if resolution_count == 0:
            issues.append({
                "type": "no_resolution_offered",
                "description": "No problem resolution approach identified",
                "severity": "medium"
            })
        
        findings.append({
            "metric": "problem_resolution",
            "score": max(0, min(100, score)),
            "details": f"Resolution indicators: {resolution_count}, Follow-up: {follow_up_count}"
        })
        
        return {
            "score": max(0, min(100, score)),
            "findings": findings,
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _calculate_confidence(self, findings: List[Dict], metric_scores: Dict[str, float]) -> float:
        """Calculate confidence in quality assessment"""
        
        # Base confidence
        confidence = 0.80
        
        # Adjust based on score consistency
        scores = list(metric_scores.values())
        if scores:
            score_variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
            if score_variance < 100:  # Low variance = high confidence
                confidence += 0.1
        
        # Adjust based on number of findings
        if len(findings) >= 5:
            confidence += 0.05
        
        return min(1.0, confidence)
```

---

## Result Aggregation Service

```python
# src/services/aggregation.py
from typing import Dict, List, Any
import statistics
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """Final aggregated analysis result"""
    analysis_id: str
    overall_score: float
    confidence: float
    categories: Dict[str, Any]
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    audit_trail: Dict[str, Any]
    execution_time: float

class ResultAggregator:
    """Aggregates results from multiple specialist agents"""
    
    async def aggregate(
        self, 
        agent_results: Dict[str, Any], 
        aggregation_rules: Dict[str, Any],
        thresholds: Dict[str, Any]
    ) -> AnalysisResult:
        """Aggregate individual agent results into final analysis"""
        
        # Extract agent scores and weights
        weighted_scores = []
        category_results = {}
        all_violations = []
        all_recommendations = []
        
        for agent_name, result in agent_results.items():
            if "error" in result:
                continue  # Skip failed agents
            
            # Get agent weight from aggregation rules
            weight = aggregation_rules.get("agent_weights", {}).get(agent_name, 1.0)
            score = result.get("score", 0)
            weighted_scores.append((score, weight))
            
            # Categorize results
            category_results[agent_name] = {
                "score": score,
                "confidence": result.get("confidence", 0.5),
                "findings": result.get("findings", []),
                "agent_version": result.get("agent_version", "unknown")
            }
            
            # Collect violations and recommendations
            all_violations.extend(result.get("violations", []))
            all_recommendations.extend(result.get("recommendations", []))
        
        # Calculate weighted overall score
        if weighted_scores:
            total_weighted_score = sum(score * weight for score, weight in weighted_scores)
            total_weight = sum(weight for _, weight in weighted_scores)
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        else:
            overall_score = 0
        
        # Calculate overall confidence
        confidences = [result.get("confidence", 0.5) for result in agent_results.values() if "error" not in result]
        overall_confidence = statistics.mean(confidences) if confidences else 0.5
        
        # Apply business rules
        final_score, final_violations, final_recommendations = self._apply_business_rules(
            overall_score, all_violations, all_recommendations, thresholds
        )
        
        # Create audit trail
        audit_trail = {
            "agents_executed": list(agent_results.keys()),
            "agents_successful": [name for name, result in agent_results.items() if "error" not in result],
            "agents_failed": [name for name, result in agent_results.items() if "error" in result],
            "aggregation_method": aggregation_rules.get("method", "weighted_average"),
            "thresholds_applied": thresholds
        }
        
        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),  # This would come from the orchestrator
            overall_score=final_score,
            confidence=overall_confidence,
            categories=category_results,
            violations=final_violations,
            recommendations=final_recommendations,
            audit_trail=audit_trail,
            execution_time=sum(result.get("execution_time", 0) for result in agent_results.values() if "error" not in result)
        )
    
    def _apply_business_rules(
        self, 
        score: float, 
        violations: List[Dict], 
        recommendations: List[Dict],
        thresholds: Dict[str, Any]
    ) -> tuple:
        """Apply business rules and thresholds to results"""
        
        final_score = score
        final_violations = violations.copy()
        final_recommendations = recommendations.copy()
        
        # Apply critical violation rules
        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        if critical_violations:
            # Critical violations cap the maximum score
            max_score_with_critical = thresholds.get("max_score_with_critical", 50)
            final_score = min(final_score, max_score_with_critical)
        
        # Apply automatic failure conditions
        failure_conditions = thresholds.get("automatic_failure", {})
        
        # Check violation count thresholds
        violation_counts = {}
        for violation in violations:
            severity = violation.get("severity", "low")
            violation_counts[severity] = violation_counts.get(severity, 0) + 1
        
        for severity, max_count in failure_conditions.get("max_violations", {}).items():
            if violation_counts.get(severity, 0) > max_count:
                final_score = 0
                final_violations.append({
                    "type": "automatic_failure",
                    "severity": "critical",
                    "description": f"Exceeded maximum {severity} violations ({violation_counts[severity]} > {max_count})",
                    "system_generated": True
                })
        
        # Apply score-based rules
        score_thresholds = thresholds.get("score_based_rules", {})
        
        if final_score < score_thresholds.get("requires_human_review", 70):
            final_recommendations.append({
                "type": "human_review_required",
                "description": "Score below threshold - requires human review",
                "priority": "high",
                "system_generated": True
            })
        
        if final_score < score_thresholds.get("automatic_rejection", 30):
            final_violations.append({
                "type": "automatic_rejection",
                "severity": "critical",
                "description": "Score below automatic rejection threshold",
                "system_generated": True
            })
        
        # Deduplicate and prioritize recommendations
        final_recommendations = self._deduplicate_recommendations(final_recommendations)
        
        return final_score, final_violations, final_recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate recommendations and prioritize"""
        
        seen_types = set()
        deduped = []
        
        # Sort by priority first
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_recommendations = sorted(
            recommendations, 
            key=lambda x: priority_order.get(x.get("priority", "low"), 3)
        )
        
        for rec in sorted_recommendations:
            rec_type = rec.get("type", "unknown")
            if rec_type not in seen_types:
                seen_types.add(rec_type)
                deduped.append(rec)
        
        return deduped
```

---

## Monitoring and Health Services

```python
# src/services/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import asyncio
from typing import Dict, Any

class MetricsCollector:
    """Collects and exposes service metrics"""
    
    def __init__(self):
        # Operational metrics
        self.analysis_requests_total = Counter(
            'analysis_requests_total',
            'Total number of analysis requests',
            ['portfolio_id', 'scorecard_id']
        )
        
        self.analysis_duration_seconds = Histogram(
            'analysis_duration_seconds',
            'Analysis execution time in seconds',
            buckets=[1, 5, 10, 30, 60, 120, 300]
        )
        
        self.agent_execution_duration = Histogram(
            'agent_execution_duration_seconds',
            'Individual agent execution time',
            ['agent_name', 'agent_type']
        )
        
        self.analysis_errors_total = Counter(
            'analysis_errors_total',
            'Total number of analysis errors',
            ['error_type']
        )
        
        # Cache metrics
        self.cache_hits_total = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
        self.cache_misses_total = Counter('cache_misses_total', 'Cache misses', ['cache_type'])
        
        # Business metrics
        self.violations_detected = Counter(
            'violations_detected_total',
            'Violations detected by type',
            ['violation_type', 'severity']
        )
        
        self.confidence_scores = Histogram(
            'confidence_scores',
            'Distribution of confidence scores',
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        )
        
        # System metrics
        self.active_analyses = Gauge('active_analyses', 'Number of analyses in progress')
        self.database_connections = Gauge('database_connections_active', 'Active database connections')
        
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        return {
            "timestamp": time.time(),
            "metrics": {
                "total_requests": self.analysis_requests_total._value.sum(),
                "active_analyses": self.active_analyses._value.get(),
                "average_duration": self._get_histogram_avg(self.analysis_duration_seconds),
                "error_rate": self._calculate_error_rate(),
                "cache_hit_rate": self._calculate_cache_hit_rate()
            }
        }
    
    def _get_histogram_avg(self, histogram) -> float:
        """Calculate average from histogram"""
        if histogram._count.sum() == 0:
            return 0.0
        return histogram._sum.sum() / histogram._count.sum()
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        total_requests = self.analysis_requests_total._value.sum()
        total_errors = self.analysis_errors_total._value.sum()
        
        if total_requests == 0:
            return 0.0
        
        return total_errors / total_requests
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_hits = self.cache_hits_total._value.sum()
        total_misses = self.cache_misses_total._value.sum()
        total_requests = total_hits + total_misses
        
        if total_requests == 0:
            return 0.0
        
        return total_hits / total_requests

# src/services/health.py
import asyncio
from typing import Dict, Any
from prisma import Prisma
import redis.asyncio as redis

class HealthChecker:
    """Service health monitoring"""
    
    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "cache": self._check_redis,
            "models": self._check_model_availability,
            "memory": self._check_memory_usage,
            "disk": self._check_disk_space
        }
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        
        results = {}
        overall_healthy = True
        
        for check_name, check_func in self.checks.items():
            try:
                result = await asyncio.wait_for(check_func(), timeout=5.0)
                results[check_name] = result
                if not result["healthy"]:
                    overall_healthy = False
            except asyncio.TimeoutError:
                results[check_name] = {
                    "healthy": False,
                    "error": "Health check timed out"
                }
                overall_healthy = False
            except Exception as e:
                results[check_name] = {
                    "healthy": False,
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": time.time(),
            "checks": results
        }
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            db = Prisma()
            await db.connect()
            
            # Simple query to verify connection
            result = await db.query_raw("SELECT 1 as test")
            
            await db.disconnect()
            
            return {
                "healthy": True,
                "response_time_ms": 0,  # Would measure actual response time
                "details": "Database connection successful"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            cache = redis.Redis()
            
            # Ping Redis
            pong = await cache.ping()
            
            # Test set/get
            test_key = "health_check_test"
            await cache.set(test_key, "test_value", ex=10)
            value = await cache.get(test_key)
            await cache.delete(test_key)
            
            return {
                "healthy": True,
                "ping_response": pong,
                "details": "Redis connection and operations successful"
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_model_availability(self) -> Dict[str, Any]:
        """Check model provider availability"""
        try:
            # This would implement actual model availability checks
            # For now, return healthy
            return {
                "healthy": True,
                "providers": {
                    "gemini": True,
                    "openai": True,
                    "anthropic": True
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            return {
                "healthy": usage_percent < 90,
                "usage_percent": usage_percent,
                "available_gb": round(memory.available / (1024**3), 2)
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            import shutil
            
            total, used, free = shutil.disk_usage("/")
            usage_percent = (used / total) * 100
            
            return {
                "healthy": usage_percent < 85,
                "usage_percent": round(usage_percent, 2),
                "free_gb": round(free / (1024**3), 2)
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
```

---

## Implementation Priorities and Next Steps

### Phase 1: Foundation (Week 1-2)
1. **Database Schema Setup**
   - Create and test Prisma schema
   - Set up development database
   - Create seed data for testing

2. **Basic API Framework**
   - FastAPI application structure
   - Authentication middleware
   - Basic health endpoints

3. **Core Orchestration**
   - Basic orchestrator class
   - Simple agent selection logic
   - Result storage

### Phase 2: Core Agents (Week 3-4)
1. **Agent Factory Implementation**
   - Database-driven agent creation
   - Model registry integration
   - Basic agent wrapping

2. **Specialist Agents**
   - Compliance specialist (FDCPA focus)
   - Quality assessment specialist
   - Basic result aggregation

3. **Redis Integration**
   - Cache implementation
   - Session management
   - Performance optimization

### Phase 3: Advanced Features (Week 5-6)
1. **Full Compliance Coverage**
   - Additional regulatory frameworks
   - Enhanced violation detection
   - Confidence scoring

2. **Quality Enhancements**
   - Advanced NLP processing
   - Better aggregation logic
   - Error handling and recovery

3. **Monitoring and Observability**
   - Metrics collection
   - Health monitoring
   - Performance tracking

### Phase 4: Production Readiness (Week 7-8)
1. **Testing and Validation**
   - Comprehensive test suite
   - Performance testing
   - Integration testing

2. **Deployment Preparation**
   - Container optimization
   - Configuration management
   - Documentation completion

3. **Production Deployment**
   - Staging environment testing
   - Production deployment
   - Monitoring setup

---

## Development Standards

### Code Quality
- Type hints for all functions
- Comprehensive docstrings
- Error handling with proper logging
- Unit test coverage > 80%

### Security
- Input validation on all endpoints
- Proper authentication and authorization
- Secure handling of API keys
- Audit logging for all operations

### Performance
- Database query optimization
- Proper caching strategies
- Async/await for I/O operations
- Connection pooling

### Monitoring
- Structured logging with correlation IDs
- Comprehensive metrics collection
- Health checks for all dependencies
- Distributed tracing support

This masterplan provides the complete blueprint for autonomous Claude Code development of the agent-engine service. The modular architecture, comprehensive implementation details, and clear development phases enable rapid, autonomous development while maintaining high quality and production readiness standards.