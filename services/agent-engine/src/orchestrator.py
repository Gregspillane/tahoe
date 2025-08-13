"""Core Orchestration Engine for agent-engine service"""

# Import ADK if available, otherwise use mocks
try:
    from google.adk.agents import Agent, ParallelAgent, SequentialAgent
except ImportError:
    # ADK not available, will use mock implementations
    Agent = object
    ParallelAgent = object
    SequentialAgent = object

import redis.asyncio as redis
from typing import Dict, List, Optional, Any
from .models.database import database_manager, retry_db_operation
import asyncio
import json
import uuid
from datetime import datetime
import os
import time
import logging

logger = logging.getLogger(__name__)


class TahoeOrchestrator:
    """Core orchestration engine for multi-agent compliance analysis"""
    
    def __init__(self):
        self.db_manager = database_manager
        self.db = None  # Will be set to database_manager.db after init
        self.cache: Optional[redis.Redis] = None
        self._initialized = False
        
        # Import these lazily to avoid circular imports
        self.agent_factory = None
        self.content_analyzer = None
        self.result_aggregator = None
        
    async def initialize(self):
        """Initialize database, cache connections, and services"""
        if self._initialized:
            return
            
        # Initialize database connection
        await self.db_manager.connect()
        self.db = self.db_manager.db
        
        # Initialize Redis client
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6382")
        self.cache = redis.from_url(redis_url, decode_responses=True)
        
        # Initialize services (lazy imports to avoid circular dependencies)
        from .agents.factory import AgentFactory
        from .services.content_analyzer import ContentAnalyzer
        from .services.aggregation import ResultAggregator
        
        self.agent_factory = AgentFactory()
        self.content_analyzer = ContentAnalyzer()
        self.result_aggregator = ResultAggregator()
        
        self._initialized = True
        
    async def cleanup(self):
        """Cleanup connections on shutdown"""
        await self.db_manager.disconnect()
        if self.cache:
            await self.cache.close()
        self._initialized = False
        
    async def analyze_interaction(
        self, 
        interaction_data: dict,
        scorecard_id: str,
        portfolio_id: str,
        options: dict = None
    ) -> 'AnalysisResult':
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
        
        # Ensure initialized
        if not self._initialized:
            await self.initialize()
        
        # Generate trace ID for monitoring
        trace_id = str(uuid.uuid4())
        
        # Create analysis record with retry for connection issues
        analysis = await retry_db_operation(
            lambda: self.db.analysis.create(
                data={
                    "interactionId": interaction_data.get("id", f"interaction-{uuid.uuid4().hex[:8]}"),
                    "portfolioId": portfolio_id,
                    "scorecardId": scorecard_id,
                    "status": "processing",
                    "traceId": trace_id,
                    "metadata": {
                        "options": options or {},
                        "interaction_type": interaction_data.get("type", "unknown")
                    }
                }
            )
        )
        
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
            await self.db.analysis.update(
                where={"id": analysis.id},
                data={
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
            )
            
            # Clean up session cache
            await self.cache.delete(f"analysis:session:{analysis.id}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Analysis failed for {analysis.id}: {str(e)}")
            
            await self.db.analysis.update(
                where={"id": analysis.id},
                data={
                    "status": "failed",
                    "metadata": {
                        "error": str(e),
                        "trace_id": trace_id
                    }
                }
            )
            
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
        scorecard = await self.db.scorecard.find_unique(
            where={"id": scorecard_id},
            include={
                "scorecardAgents": {
                    "include": {"agent": True}
                }
            }
        )
        
        if not scorecard:
            raise ValueError(f"Scorecard {scorecard_id} not found")
        
        # Convert to dict for caching (handle datetime serialization)
        scorecard_dict = {
            "id": scorecard.id,
            "name": scorecard.name,
            "description": scorecard.description,
            "portfolioId": scorecard.portfolioId,
            "version": scorecard.version,
            "requirements": scorecard.requirements,
            "thresholds": scorecard.thresholds,
            "aggregationRules": scorecard.aggregationRules,
            "isActive": scorecard.isActive,
            "scorecardAgents": [
                {
                    "id": sa.id,
                    "scorecardId": sa.scorecardId,
                    "agentId": sa.agentId,
                    "weight": sa.weight,
                    "isRequired": sa.isRequired,
                    "configuration": sa.configuration,
                    "executionOrder": sa.executionOrder,
                    "agent": {
                        "id": sa.agent.id,
                        "name": sa.agent.name,
                        "description": sa.agent.description,
                        "type": sa.agent.type,
                        "model": sa.agent.model,
                        "modelConfig": sa.agent.modelConfig,
                        "capabilities": sa.agent.capabilities,
                        "tools": sa.agent.tools,
                        "triggerRules": sa.agent.triggerRules,
                        "systemPrompt": sa.agent.systemPrompt,
                        "userPrompt": sa.agent.userPrompt,
                        "version": sa.agent.version,
                        "isActive": sa.agent.isActive
                    }
                }
                for sa in scorecard.scorecardAgents
            ]
        }
        
        # Cache for next time
        await self.cache.setex(
            f"scorecard:{scorecard_id}",
            300,  # 5 minutes
            json.dumps(scorecard_dict)
        )
        
        return scorecard_dict
    
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
        
        # If no trigger rules, always activate
        if not trigger_rules:
            return True
        
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
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[dict]:
        """
        Get real-time status of an analysis from Redis cache
        
        Args:
            analysis_id: The analysis ID to check
            
        Returns:
            Status information if found, None otherwise
        """
        if not self._initialized:
            await self.initialize()
            
        session_key = f"analysis:session:{analysis_id}"
        session_data = await self.cache.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        
        # Fallback to database
        analysis = await self.db.analysis.find_unique(
            where={"id": analysis_id}
        )
        
        if analysis:
            return {
                "status": analysis.status,
                "phase": "completed" if analysis.status == "complete" else "unknown",
                "started_at": analysis.createdAt.isoformat(),
                "completed_at": analysis.completedAt.isoformat() if analysis.completedAt else None,
                "trace_id": analysis.traceId
            }
        
        return None
    
    async def warmup_caches(self):
        """Pre-populate frequently used cache entries"""
        if not self._initialized:
            await self.initialize()
            
        # Load active agent templates into cache
        templates = await self.db.agenttemplate.find_many(
            where={"isActive": True}
        )
        
        for template in templates:
            cache_key = f"agent:template:{template.id}"
            template_dict = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "type": template.type,
                "model": template.model,
                "modelConfig": template.modelConfig,
                "capabilities": template.capabilities,
                "tools": template.tools,
                "triggerRules": template.triggerRules,
                "systemPrompt": template.systemPrompt,
                "userPrompt": template.userPrompt,
                "version": template.version,
                "isActive": template.isActive
            }
            await self.cache.setex(
                cache_key,
                300,  # 5 minutes
                json.dumps(template_dict)
            )
        
        logger.info(f"Warmed up cache with {len(templates)} agent templates")
        return len(templates)