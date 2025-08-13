"""Agent Factory for creating ADK agents from database templates"""

# Import ADK components with fallback for development
try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import tool
except ImportError:
    # Development fallback - will be replaced with real ADK
    class LlmAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        async def run(self, input=None, system=None):
            return f"Mock response for: {input}"
    
    def tool(func):
        return func

from typing import Dict, Any, Optional, List
import json
import redis.asyncio as redis
from prisma import Prisma
import logging
import time

from .base import BaseSpecialistAgent, AgentResult
from ..models.registry import ModelRegistry, ModelConfig
from ..tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating ADK agents from database templates"""
    
    def __init__(self, db: Prisma = None, cache: redis.Redis = None):
        self.db = db
        self.cache = cache
        self.model_registry = ModelRegistry()
        self.tool_registry = ToolRegistry()
        
    async def initialize(self):
        """Initialize database and cache connections"""
        if not self.db:
            self.db = Prisma()
            await self.db.connect()
        
        if not self.cache:
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6382")
            self.cache = redis.from_url(redis_url, decode_responses=True)
    
    async def create_agent(self, template: dict) -> 'TahoeAgent':
        """
        Create an ADK agent from a template configuration
        
        Args:
            template: Agent template configuration from database
            
        Returns:
            TahoeAgent wrapper around ADK LlmAgent
            
        Raises:
            ValueError: If template is invalid or model not supported
        """
        try:
            logger.info(f"Creating agent from template: {template.get('name', 'unknown')}")
            
            # Get model configuration
            model_config = self.model_registry.get_config(
                template["model"],
                template.get("modelConfig", {})
            )
            
            # Load tools
            tools = await self.tool_registry.load_tools(template.get("tools", []))
            
            # Create ADK LlmAgent with verified parameters
            adk_agent = LlmAgent(
                name=template["name"],
                model=model_config.model_string,
                description=template.get("description", ""),
                instruction=template.get("systemPrompt", ""),
                tools=tools,
                **model_config.parameters
            )
            
            # Wrap in TahoeAgent for additional functionality
            return TahoeAgent(
                adk_agent=adk_agent,
                template=template,
                factory=self
            )
            
        except Exception as e:
            logger.error(f"Failed to create agent from template {template.get('id', 'unknown')}: {str(e)}")
            raise ValueError(f"Agent creation failed: {str(e)}")
    
    async def load_template(self, template_id: str) -> dict:
        """Load agent template with caching and error handling"""
        
        try:
            # Ensure initialized
            if not self.cache:
                await self.initialize()
            
            # Check cache first
            cache_key = f"agent:template:{template_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for template {template_id}")
                return json.loads(cached)
            
            # Load from database
            template = await self.db.agenttemplate.find_unique({
                "where": {"id": template_id}
            })
            
            if not template:
                raise TemplateNotFoundError(f"Agent template {template_id} not found")
            
            if not template.isActive:
                raise ValueError(f"Agent template {template_id} is inactive")
            
            # Convert to dict for caching
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
            
            # Cache for reuse
            await self.cache.setex(
                cache_key,
                300,  # 5 minutes TTL
                json.dumps(template_dict, default=str)
            )
            
            logger.debug(f"Loaded and cached template {template_id}")
            return template_dict
            
        except Exception as e:
            logger.error(f"Failed to load template {template_id}: {str(e)}")
            raise
    
    async def invalidate_cache(self, template_id: str):
        """Invalidate cached template"""
        if self.cache:
            await self.cache.delete(f"agent:template:{template_id}")
            logger.debug(f"Invalidated cache for template {template_id}")


class TemplateNotFoundError(Exception):
    """Raised when an agent template is not found"""
    pass


class TahoeAgent:
    """Wrapper around ADK agent with Tahoe-specific functionality"""
    
    def __init__(self, adk_agent: LlmAgent, template: dict, factory: AgentFactory):
        self.adk_agent = adk_agent
        self.template = template
        self.factory = factory
        
    async def analyze(self, input_data: dict) -> AgentResult:
        """Execute analysis with Tahoe-specific processing"""
        
        start_time = time.time()
        
        try:
            # Prepare prompts
            system_prompt = self.template.get("systemPrompt", "")
            user_prompt = self._build_user_prompt(input_data)
            
            # Execute ADK agent
            result = await self.adk_agent.run(
                input=user_prompt,
                system=system_prompt
            )
            
            # Process and structure result
            processed_result = self._process_result(result, input_data)
            
            execution_time = time.time() - start_time
            
            return AgentResult(
                agent_name=self.template["name"],
                agent_version=str(self.template["version"]),
                score=processed_result.get("score", 0.0),
                confidence=processed_result.get("confidence", 0.0),
                findings=processed_result.get("findings", []),
                violations=processed_result.get("violations", []),
                recommendations=processed_result.get("recommendations", []),
                execution_time=execution_time,
                metadata={
                    "model_used": self.template["model"],
                    "trace_id": input_data.get("trace_id"),
                    "template_version": self.template["version"]
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent {self.template['name']} analysis failed: {str(e)}")
            
            # Return error result
            return AgentResult(
                agent_name=self.template["name"],
                agent_version=str(self.template["version"]),
                score=0.0,
                confidence=0.0,
                findings=[],
                violations=[],
                recommendations=[],
                execution_time=execution_time,
                metadata={
                    "error": str(e),
                    "trace_id": input_data.get("trace_id")
                }
            )
    
    def _build_user_prompt(self, input_data: dict) -> str:
        """Build user prompt from template and input data"""
        
        base_prompt = self.template.get("userPrompt", "")
        
        # Template variable substitution with error handling
        try:
            if base_prompt:
                return base_prompt.format(
                    interaction=input_data.get("interaction", {}),
                    configuration=input_data.get("configuration", {}),
                    context=input_data.get("context", {})
                )
        except KeyError as e:
            logger.warning(f"Template variable {e} not found in input data")
        
        # Fallback to interaction content
        interaction = input_data.get("interaction", {})
        content = interaction.get("content", "")
        interaction_type = interaction.get("type", "unknown")
        
        return f"Analyze this {interaction_type} interaction:\n\n{content}"
    
    def _process_result(self, result: Any, input_data: dict) -> dict:
        """Process ADK agent result into standardized format"""
        
        # Basic result processing - this would be enhanced based on actual ADK output format
        if isinstance(result, str):
            # Parse string response for basic metrics
            confidence = self._calculate_confidence(result)
            
            return {
                "score": self._extract_score(result),
                "confidence": confidence,
                "findings": self._extract_findings(result),
                "violations": self._extract_violations(result),
                "recommendations": self._extract_recommendations(result)
            }
        elif isinstance(result, dict):
            # Use structured response if available
            return {
                "score": result.get("score", 0.0),
                "confidence": result.get("confidence", self._calculate_confidence(result)),
                "findings": result.get("findings", []),
                "violations": result.get("violations", []),
                "recommendations": result.get("recommendations", [])
            }
        else:
            # Fallback for unknown result types
            return {
                "score": 0.0,
                "confidence": 0.5,
                "findings": [],
                "violations": [],
                "recommendations": []
            }
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence score for the result using basic heuristics"""
        
        if isinstance(result, str):
            # Basic confidence heuristics
            if len(result) < 50:
                return 0.3  # Very short responses are less confident
            elif "uncertain" in result.lower() or "maybe" in result.lower():
                return 0.6  # Explicit uncertainty indicators
            elif "confident" in result.lower() or "certain" in result.lower():
                return 0.9  # Explicit confidence indicators
            else:
                return 0.85  # Default moderate confidence
        elif isinstance(result, dict) and "confidence" in result:
            return float(result["confidence"])
        else:
            return 0.85  # Default heuristic
    
    def _extract_score(self, result: str) -> float:
        """Extract numerical score from text result"""
        import re
        
        # Look for score patterns like "Score: 85" or "85%" or "8.5/10"
        score_patterns = [
            r'score[:\s]+([0-9]+(?:\.[0-9]+)?)',
            r'([0-9]+(?:\.[0-9]+)?)%',
            r'([0-9]+(?:\.[0-9]+)?)/10',
            r'rating[:\s]+([0-9]+(?:\.[0-9]+)?)',
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, result.lower())
            if match:
                score = float(match.group(1))
                # Normalize to 0-100 scale
                if score <= 1.0:
                    return score * 100
                elif score <= 10.0:
                    return score * 10
                else:
                    return min(score, 100.0)
        
        return 0.0  # No score found
    
    def _extract_findings(self, result: str) -> List[Dict[str, Any]]:
        """Extract findings from text result"""
        # Simple implementation - would be enhanced for specific agent types
        return [{"summary": result[:200] + "..." if len(result) > 200 else result}]
    
    def _extract_violations(self, result: str) -> List[Dict[str, Any]]:
        """Extract violations from text result"""
        violations = []
        
        # Look for violation indicators
        violation_terms = ["violation", "breach", "non-compliant", "infraction", "error"]
        
        for term in violation_terms:
            if term in result.lower():
                violations.append({
                    "type": "detected_violation",
                    "severity": "medium",
                    "description": f"Potential {term} detected in analysis"
                })
                break  # Only add one generic violation
        
        return violations
    
    def _extract_recommendations(self, result: str) -> List[Dict[str, Any]]:
        """Extract recommendations from text result"""
        recommendations = []
        
        # Look for recommendation indicators
        rec_terms = ["recommend", "suggest", "should", "improve", "consider"]
        
        for term in rec_terms:
            if term in result.lower():
                recommendations.append({
                    "category": "general",
                    "priority": "medium",
                    "action": f"Review analysis for {term} guidance"
                })
                break  # Only add one generic recommendation
        
        return recommendations