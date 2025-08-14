"""
Universal Agent Factory for creating ADK agents from specifications.
Implements R2-T01: Agent Factory Base with correct ADK patterns.
"""

from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging

# CORRECTED: Proper ADK imports per official documentation
try:
    from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
    from google.adk.tools import FunctionTool
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    ADK_AVAILABLE = True
except ImportError:
    # Fallback for development without ADK
    ADK_AVAILABLE = False
    
    # Mock classes for development
    class LlmAgent:
        def __init__(self, name, model, instruction, description="", tools=None, **kwargs):
            self.name = name
            self.model = model
            self.instruction = instruction
            self.description = description
            self.tools = tools or []
    
    class SequentialAgent:
        def __init__(self, name, sub_agents, description="", **kwargs):
            self.name = name
            self.sub_agents = sub_agents
            self.description = description
    
    class ParallelAgent:
        def __init__(self, name, sub_agents, description="", **kwargs):
            self.name = name
            self.sub_agents = sub_agents
            self.description = description
    
    class LoopAgent:
        def __init__(self, name, sub_agents, description="", **kwargs):
            self.name = name
            self.sub_agents = sub_agents
            self.description = description
    
    class BaseAgent:
        pass
    
    class FunctionTool:
        def __init__(self, func):
            self.func = func
    
    class InMemoryRunner:
        def __init__(self, agent, app_name):
            self.agent = agent
            self.app_name = app_name
            self._session_service = InMemorySessionService()
        
        @property
        def session_service(self):
            return self._session_service
    
    class InMemorySessionService:
        pass

# Import specification system
try:
    from .specifications import SpecificationParser, SpecificationValidator
except ImportError:
    # Fallback for testing
    class SpecificationLoader:
        def load(self, name: str) -> Dict:
            raise NotImplementedError("SpecificationLoader not available")
    
    class SpecificationValidator:
        def validate(self, spec: Any) -> bool:
            return True

logger = logging.getLogger(__name__)


class AgentSpec(BaseModel):
    """Pydantic model for agent specifications"""
    api_version: str = Field(default="agent-engine/v1")
    kind: str = Field(default="AgentSpec")
    metadata: Dict[str, Any]
    spec: Dict[str, Any]
    
    @validator('api_version')
    def validate_version(cls, v):
        if not v.startswith("agent-engine/"):
            raise ValueError(f"Unsupported API version: {v}")
        return v
        
    @validator('kind')
    def validate_kind(cls, v):
        if v != "AgentSpec":
            raise ValueError(f"Invalid kind: {v}, expected AgentSpec")
        return v


class AgentContext(BaseModel):
    """Runtime context for agent creation"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: str = "development"
    variables: Dict[str, Any] = Field(default_factory=dict)
    parent_agent: Optional[str] = None


class AgentBuilder(ABC):
    """Abstract base class for agent builders"""
    
    @abstractmethod
    def can_build(self, agent_type: str) -> bool:
        """Check if this builder can handle the agent type"""
        pass
        
    @abstractmethod
    def build(self, spec: AgentSpec, context: AgentContext) -> BaseAgent:
        """Build the agent from specification"""
        pass
        
    @abstractmethod
    def validate_spec(self, spec: AgentSpec) -> bool:
        """Validate the specification for this agent type"""
        pass


class ToolRegistry:
    """Tool registry interface (stub for integration)."""
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get tool by name."""
        return self.tools.get(name)


class SpecificationLoader:
    """Loads specifications from various sources"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or "specs"
        self.cache: Dict[str, Dict] = {}
        
    def load(self, spec_name: str) -> Dict:
        """Load specification by name"""
        if spec_name in self.cache:
            return self.cache[spec_name]
            
        # For now, delegate to the existing specification parser
        try:
            from .specifications import SpecificationParser
            parser = SpecificationParser()
            spec_data = parser.load_agent_spec(spec_name)
            self.cache[spec_name] = spec_data
            return spec_data
        except Exception as e:
            raise ValueError(f"Specification not found: {spec_name}")


class SpecificationValidator:
    """Validates agent specifications"""
    
    def __init__(self):
        pass
        
    def validate(self, spec: Any) -> bool:
        """Validate specification structure"""
        # For now, basic validation
        if hasattr(spec, 'dict'):
            spec_dict = spec.dict()
        else:
            spec_dict = spec
            
        # Check required fields
        required_fields = ['api_version', 'kind', 'metadata', 'spec']
        for field in required_fields:
            if field not in spec_dict:
                return False
                
        return True


class UniversalAgentFactory:
    """Main factory for creating agents from specifications"""
    
    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.specs: Dict[str, AgentSpec] = {}
        self.spec_loader = SpecificationLoader()
        self.validator = SpecificationValidator()
        self.tool_registry = tool_registry
    
    def build_agent(self, spec_name: str, context: Optional[AgentContext] = None) -> BaseAgent:
        """Build an agent from specification name"""
        if context is None:
            context = AgentContext()
            
        # Load specification
        spec = self.load_spec(spec_name)
        
        # Validate specification
        if not self.validator.validate(spec):
            raise ValueError(f"Invalid specification: {spec_name}")
        
        # Direct dispatch per MASTERPLAN lines 379-388, 921-930
        agent_type = spec.spec.get("agent", {}).get("type", "llm")
        
        # Direct factory dispatch without separate builders
        if agent_type == "llm":
            return self._build_llm_agent(spec, context)
        elif agent_type == "sequential":
            return self._build_sequential_agent(spec, context)
        elif agent_type == "parallel":
            return self._build_parallel_agent(spec, context)
        elif agent_type == "loop":
            return self._build_loop_agent(spec, context)
        elif agent_type == "custom":
            return self._build_custom_agent(spec, context)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    def _build_llm_agent(self, spec: AgentSpec, context: AgentContext) -> LlmAgent:
        """Build LLM agent with dynamic configuration."""
        agent_spec = spec.spec.get("agent", {})
        tools = self._load_tools(spec.spec.get("tools", []))
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        
        # Dynamic instruction building with context injection
        instruction = self._build_instruction(
            agent_spec.get("instruction_template", ""),
            context
        )
        
        # Handle model configuration per MASTERPLAN line 401, 943
        model_config = agent_spec.get("model", {})
        model = model_config.get("primary", "gemini-2.0-flash") if isinstance(model_config, dict) else model_config
        
        return LlmAgent(
            name=spec.metadata["name"].replace("-", "_"),  # CORRECTED: Ensure underscores
            model=model,
            instruction=instruction,
            description=spec.metadata.get("description", ""),
            tools=tools,
            sub_agents=sub_agents,
            **agent_spec.get("parameters", {})
        )
    
    def _build_sequential_agent(self, spec: AgentSpec, context: AgentContext) -> SequentialAgent:
        """Build sequential workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return SequentialAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", "")
        )
    
    def _build_parallel_agent(self, spec: AgentSpec, context: AgentContext) -> ParallelAgent:
        """Build parallel workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return ParallelAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", "")
        )
    
    def _build_loop_agent(self, spec: AgentSpec, context: AgentContext) -> LoopAgent:
        """Build loop workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return LoopAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", "")
        )
    
    def _build_custom_agent(self, spec: AgentSpec, context: AgentContext) -> BaseAgent:
        """Build custom agent from specification."""
        # Placeholder for custom agent building logic
        raise NotImplementedError("Custom agent building to be implemented")
    
    def _build_instruction(self, template: str, context: AgentContext) -> str:
        """Build instruction from template with context injection."""
        if not template:
            return ""
        
        # Simple variable substitution from context
        instruction = template
        for key, value in context.variables.items():
            instruction = instruction.replace(f"{{{key}}}", str(value))
        
        return instruction
    
    def _load_tools(self, tool_specs: List[Dict]) -> List:
        """Load tools from specifications."""
        if not self.tool_registry:
            return []
        
        tools = []
        for tool_spec in tool_specs:
            if tool_spec.get("source") == "registry":
                tool = self.tool_registry.get_tool(tool_spec["name"])
                if tool:
                    tools.append(tool)
            # Handle inline and import sources in future
        
        return tools
    
    def _build_sub_agents(self, sub_agent_specs: List[Dict], context: AgentContext) -> List[BaseAgent]:
        """Build sub-agents from specifications."""
        sub_agents = []
        for sub_spec in sub_agent_specs:
            spec_ref = sub_spec.get("spec_ref")
            if spec_ref:
                # Recursive agent building
                sub_agent = self.build_agent(spec_ref, context)
                sub_agents.append(sub_agent)
        
        return sub_agents
        
    def load_spec(self, spec_name: str) -> AgentSpec:
        """Load specification by name"""
        if spec_name in self.specs:
            return self.specs[spec_name]
            
        spec_data = self.spec_loader.load(spec_name)
        spec = AgentSpec(**spec_data)
        self.specs[spec_name] = spec
        return spec
        
    def build_agent_from_dict(self, spec_dict: Dict, context: Optional[AgentContext] = None) -> BaseAgent:
        """Build an agent directly from dictionary specification"""
        if context is None:
            context = AgentContext()
            
        spec = AgentSpec(**spec_dict)
        
        if not self.validator.validate(spec):
            raise ValueError("Invalid specification dictionary")
        
        agent_type = spec.spec.get("agent", {}).get("type", "llm")
        
        # Direct dispatch
        if agent_type == "llm":
            return self._build_llm_agent(spec, context)
        elif agent_type == "sequential":
            return self._build_sequential_agent(spec, context)
        elif agent_type == "parallel":
            return self._build_parallel_agent(spec, context)
        elif agent_type == "loop":
            return self._build_loop_agent(spec, context)
        elif agent_type == "custom":
            return self._build_custom_agent(spec, context)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
    def list_supported_types(self) -> List[str]:
        """List all supported agent types"""
        return ["llm", "sequential", "parallel", "loop", "custom"]
        
    def clear_cache(self):
        """Clear cached specifications"""
        self.specs.clear()
        logger.info("Cleared specification cache")


# Backward compatibility alias
class AgentCompositionService:
    """Service to compose agents from specifications - backward compatibility."""
    
    def __init__(self, tool_registry: Optional[Dict[str, Any]] = None):
        """Initialize composition service."""
        registry = ToolRegistry() if tool_registry else None
        if tool_registry and registry:
            registry.tools = tool_registry
        self.factory = UniversalAgentFactory(tool_registry=registry)
    
    def build_agent_from_spec(self, spec_name: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Build agent from specification name."""
        agent_context = AgentContext(variables=context or {})
        return self.factory.build_agent(spec_name, agent_context)