"""
Universal Agent Factory for creating ADK agents from specifications.
Implements R2-T01: Agent Factory Base with correct ADK patterns.
"""

from typing import Dict, Any, Optional, List, Type, AsyncGenerator
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, validator
import logging
import yaml
import inspect
from pathlib import Path

# Real ADK imports - no fallbacks, fail-fast approach
from google.adk.agents import (
    LlmAgent,
    SequentialAgent,
    ParallelAgent,
    LoopAgent,
    BaseAgent,
)
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext


# Import specification system
try:
    from .specifications import SpecificationValidator
except ImportError:
    # Fallback for testing
    class SpecificationLoader:
        def load(self, name: str) -> Dict:
            raise NotImplementedError("SpecificationLoader not available")

    class SpecificationValidator:
        def validate(self, spec: Any) -> bool:
            return True


logger = logging.getLogger(__name__)


class SpecificationError(Exception):
    """Exception raised for specification-related errors"""

    pass


class AgentSpec(BaseModel):
    """Pydantic model for agent specifications"""

    api_version: str = Field(default="agent-engine/v1")
    kind: str = Field(default="AgentSpec")
    metadata: Dict[str, Any]
    spec: Dict[str, Any]

    @validator("api_version")
    def validate_version(cls, v):
        if not v.startswith("agent-engine/"):
            raise ValueError(f"Unsupported API version: {v}")
        return v

    @validator("kind")
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
        except Exception:
            raise ValueError(f"Specification not found: {spec_name}")


class SpecificationValidator:
    """Validates agent specifications"""

    def __init__(self):
        pass

    def validate(self, spec: Any) -> bool:
        """Validate specification structure"""
        # For now, basic validation
        if hasattr(spec, "dict"):
            spec_dict = spec.dict()
        else:
            spec_dict = spec

        # Check required fields
        required_fields = ["api_version", "kind", "metadata", "spec"]
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
        self.builders: Dict[str, AgentBuilder] = {}
        self.custom_registry: Dict[
            str, Type[BaseAgent]
        ] = {}  # Registry for custom agent classes
        self._register_builders()
        self._load_custom_agents()

    def _register_builders(self):
        """Register agent builders for different types"""
        try:
            from .builders import LlmAgentBuilder

            llm_builder = LlmAgentBuilder(self.tool_registry)
            llm_builder.sub_agent_factory = self  # Set back-reference for sub-agents
            self.builders["llm"] = llm_builder
            self.builders["agent"] = llm_builder  # LlmAgent is aliased as Agent
        except ImportError:
            # LlmAgentBuilder not available yet, use fallback
            pass

        try:
            from .builders import (
                SequentialAgentBuilder,
                ParallelAgentBuilder,
                LoopAgentBuilder,
            )

            # Register workflow builders with factory reference
            sequential_builder = SequentialAgentBuilder(factory=self)
            parallel_builder = ParallelAgentBuilder(factory=self)
            loop_builder = LoopAgentBuilder(factory=self)

            self.builders["sequential"] = sequential_builder
            self.builders["parallel"] = parallel_builder
            self.builders["loop"] = loop_builder

        except ImportError:
            # Workflow builders not available yet, use fallback
            pass

    def build_agent(
        self, spec_name: str, context: Optional[AgentContext] = None
    ) -> BaseAgent:
        """Build an agent from specification name"""
        if context is None:
            context = AgentContext()

        # Load specification
        spec = self.load_spec(spec_name)

        # Validate specification
        if not self.validator.validate(spec):
            raise ValueError(f"Invalid specification: {spec_name}")

        agent_type = spec.spec.get("agent", {}).get("type", "llm")

        # Use builder if available, otherwise fallback to direct dispatch
        if agent_type in self.builders:
            builder = self.builders[agent_type]
            return builder.build(spec, context)
        else:
            # Fallback to direct dispatch for types without builders
            if agent_type == "sequential":
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
            agent_spec.get("instruction_template", ""), context
        )

        # Handle model configuration per MASTERPLAN line 401, 943
        model_config = agent_spec.get("model", {})
        model = (
            model_config.get("primary", "gemini-2.0-flash")
            if isinstance(model_config, dict)
            else model_config
        )

        return LlmAgent(
            name=spec.metadata["name"].replace(
                "-", "_"
            ),  # CORRECTED: Ensure underscores
            model=model,
            instruction=instruction,
            description=spec.metadata.get("description", ""),
            tools=tools,
            sub_agents=sub_agents,
            **agent_spec.get("parameters", {}),
        )

    def _build_sequential_agent(
        self, spec: AgentSpec, context: AgentContext
    ) -> SequentialAgent:
        """Build sequential workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return SequentialAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", ""),
        )

    def _build_parallel_agent(
        self, spec: AgentSpec, context: AgentContext
    ) -> ParallelAgent:
        """Build parallel workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return ParallelAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", ""),
        )

    def _build_loop_agent(self, spec: AgentSpec, context: AgentContext) -> LoopAgent:
        """Build loop workflow agent."""
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)
        return LoopAgent(
            name=spec.metadata["name"].replace("-", "_"),
            sub_agents=sub_agents,
            description=spec.metadata.get("description", ""),
        )

    def _build_custom_agent(self, spec: AgentSpec, context: AgentContext) -> BaseAgent:
        """Build custom agent from specification.

        Integrated into universal factory pattern following ADK patterns.
        """
        agent_spec = spec.spec.get("agent", {})
        custom_class_name = agent_spec.get("custom_class")

        if not custom_class_name:
            raise SpecificationError(
                "Custom agent specification needs 'custom_class' field"
            )

        # Get registered custom agent class
        agent_class = self.custom_registry.get(custom_class_name)
        if not agent_class:
            raise SpecificationError(
                f"Custom agent class '{custom_class_name}' not registered"
            )

        # Validate it inherits from BaseAgent
        if not issubclass(agent_class, BaseAgent):
            raise SpecificationError(f"{custom_class_name} must inherit from BaseAgent")

        # Build sub-agents if specified
        sub_agents = self._build_sub_agents(spec.spec.get("sub_agents", []), context)

        # Get initialization parameters from spec
        init_params = agent_spec.get("parameters", {}).copy()
        init_params["name"] = spec.metadata["name"].replace(
            "-", "_"
        )  # ADK naming pattern
        init_params["description"] = spec.metadata.get("description", "")

        # Only add sub_agents if the class expects them
        if sub_agents:
            init_params["sub_agents"] = sub_agents

        # Add context variables if provided
        if context and context.variables:
            # Merge context variables but don't override spec parameters
            for key, value in context.variables.items():
                if key not in init_params:
                    init_params[key] = value

        # Create instance
        try:
            agent = agent_class(**init_params)
            logger.info(
                f"Built custom agent: {spec.metadata['name']} (class: {custom_class_name})"
            )
            return agent
        except Exception as e:
            raise SpecificationError(
                f"Error creating custom agent '{custom_class_name}': {e}"
            )

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

    def _build_sub_agents(
        self, sub_agent_specs: List[Dict], context: AgentContext
    ) -> List[BaseAgent]:
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

    def build_agent_from_dict(
        self, spec_dict: Dict, context: Optional[AgentContext] = None
    ) -> BaseAgent:
        """Build an agent directly from dictionary specification"""
        if context is None:
            context = AgentContext()

        spec = AgentSpec(**spec_dict)

        if not self.validator.validate(spec):
            raise ValueError("Invalid specification dictionary")

        agent_type = spec.spec.get("agent", {}).get("type", "llm")

        # Use builder if available, otherwise fallback to direct dispatch
        if agent_type in self.builders:
            builder = self.builders[agent_type]
            return builder.build(spec, context)
        else:
            # Fallback to direct dispatch for types without builders
            if agent_type == "sequential":
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

    def register_custom_agent(self, name: str, agent_class: Type[BaseAgent]):
        """Register a custom agent class for use in specifications.

        Registration method for custom agents following ADK patterns.
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"{agent_class} must inherit from BaseAgent")

        # Verify required method is overridden (not just inherited from BaseAgent)
        if "_run_async_impl" not in agent_class.__dict__:
            raise ValueError(f"{agent_class} must override _run_async_impl method")

        # Verify method signature
        sig = inspect.signature(agent_class._run_async_impl)
        if len(sig.parameters) < 2:  # self + ctx
            raise ValueError(
                f"{agent_class}._run_async_impl must accept InvocationContext parameter"
            )

        self.custom_registry[name] = agent_class
        logger.info(f"Registered custom agent class: {name}")

    def _load_custom_agents(self):
        """Load custom agent definitions from specifications.

        Load built-in custom agents and spec files if directory exists.
        """
        # First, register built-in custom agents
        try:
            from .custom_agents import register_built_in_agents

            register_built_in_agents(self)
        except ImportError:
            logger.warning("Built-in custom agents module not available")

        # Then load custom agents from spec files
        custom_specs_dir = Path("specs/agents/custom")
        if not custom_specs_dir.exists():
            logger.debug("Custom agents directory does not exist: specs/agents/custom")
            return

        for spec_file in custom_specs_dir.glob("*.yaml"):
            try:
                with open(spec_file) as f:
                    spec = yaml.safe_load(f)

                # Check if it defines a custom agent implementation
                if spec.get("implementation"):
                    self._register_custom_from_spec(spec)
                    logger.info(f"Loaded custom agent spec from {spec_file}")
            except Exception as e:
                logger.warning(f"Error loading custom agent spec {spec_file}: {e}")

    def _register_custom_from_spec(self, spec: dict):
        """Register custom agent from specification with implementation.

        Support specification-based custom agent registration.
        """
        implementation = spec.get("implementation", {})
        class_definition = implementation.get("class_definition")

        if class_definition:
            # Create class dynamically from specification
            namespace = {
                "BaseAgent": BaseAgent,
                "Event": Event,
                "InvocationContext": InvocationContext,
                "AsyncGenerator": AsyncGenerator,
                "List": List,
                "Dict": Dict,
                "Any": Any,
                "Optional": Optional,
                "logging": logging,
            }

            try:
                exec(class_definition, namespace)

                class_name = implementation.get("class_name")
                if class_name and class_name in namespace:
                    self.register_custom_agent(class_name, namespace[class_name])
                    logger.info(f"Dynamically registered custom agent: {class_name}")
                else:
                    logger.warning(
                        f"Class name '{class_name}' not found in implementation"
                    )
            except Exception as e:
                logger.error(f"Error executing custom agent class definition: {e}")

    def list_custom_agents(self) -> List[str]:
        """List all registered custom agent classes"""
        return list(self.custom_registry.keys())


# Backward compatibility alias
class AgentCompositionService:
    """Service to compose agents from specifications - backward compatibility."""

    def __init__(self, tool_registry: Optional[Dict[str, Any]] = None):
        """Initialize composition service."""
        registry = ToolRegistry() if tool_registry else None
        if tool_registry and registry:
            registry.tools = tool_registry
        self.factory = UniversalAgentFactory(tool_registry=registry)

    def build_agent_from_spec(
        self, spec_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Build agent from specification name."""
        agent_context = AgentContext(variables=context or {})
        return self.factory.build_agent(spec_name, agent_context)
