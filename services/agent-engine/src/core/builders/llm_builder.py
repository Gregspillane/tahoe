from google.adk.agents import LlmAgent, Agent
from google.adk.tools import FunctionTool, google_search
from typing import List, Dict, Any, Optional, Callable
import inspect
import re
from string import Template
import logging
from datetime import datetime

from ..composition import AgentBuilder, AgentSpec, AgentContext
from ..specification import SpecificationError

logger = logging.getLogger(__name__)

class ToolLoader:
    """Loads and validates tools for agents"""
    
    def __init__(self, tool_registry=None):
        self.tool_registry = tool_registry
        self.built_in_tools = self._load_built_in_tools()
    
    def load_tools(self, tool_specs: List[Dict]) -> List[Callable]:
        """Load tools from specifications"""
        tools = []
        
        for spec in tool_specs:
            tool = self._load_single_tool(spec)
            if tool:
                tools.append(tool)
            else:
                logger.warning(f"Failed to load tool: {spec.get('name', 'unknown')}")
        
        return tools
    
    def _load_single_tool(self, spec: Dict) -> Optional[Callable]:
        """Load a single tool from specification"""
        source = spec.get('source', 'registry')
        
        if source == 'registry':
            return self._load_from_registry(spec['name'])
        elif source == 'builtin':
            return self._load_built_in(spec['name'])
        elif source == 'inline':
            return self._create_inline_tool(spec)
        elif source == 'import':
            return self._import_tool(spec)
        else:
            logger.error(f"Unknown tool source: {source}")
            return None
    
    def _load_from_registry(self, name: str) -> Optional[Callable]:
        """Load tool from registry"""
        if not self.tool_registry:
            logger.warning("No tool registry available")
            return None
        
        return self.tool_registry.get_tool(name)
    
    def _load_built_in(self, name: str) -> Optional[Callable]:
        """Load built-in ADK tool"""
        # Proper handling of google_search
        if name == "google_search":
            try:
                return google_search
            except Exception as e:
                logger.error(f"google_search tool not available: {e}")
                return None
        
        return self.built_in_tools.get(name)
    
    def _create_inline_tool(self, spec: Dict) -> Optional[Callable]:
        """Create tool from inline definition"""
        try:
            definition = spec.get('definition', '')
            # Create local namespace for execution
            namespace = {}
            exec(definition, namespace)
            
            # Find the function in namespace
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith('_'):
                    return obj
            
            logger.error("No callable found in inline definition")
            return None
            
        except Exception as e:
            logger.error(f"Error creating inline tool: {e}")
            return None
    
    def _import_tool(self, spec: Dict) -> Optional[Callable]:
        """Import tool from module"""
        try:
            module_name = spec.get('module')
            function_name = spec.get('function')
            
            module = __import__(module_name, fromlist=[function_name])
            return getattr(module, function_name)
            
        except Exception as e:
            logger.error(f"Error importing tool: {e}")
            return None
    
    def _load_built_in_tools(self) -> Dict[str, Callable]:
        """Load available built-in tools"""
        tools = {}
        # Include google_search in built-in tools
        try:
            tools['google_search'] = google_search
        except Exception:
            pass  # google_search may not be available in all environments
        return tools
    
    def validate_tool(self, tool: Callable) -> bool:
        """Validate tool has proper signature"""
        try:
            sig = inspect.signature(tool)
            # Basic validation - has parameters and returns something
            return len(sig.parameters) > 0
        except Exception:
            return False

class LlmAgentBuilder(AgentBuilder):
    """Builder for LlmAgent instances"""
    
    def __init__(self, tool_registry=None):
        self.tool_loader = ToolLoader(tool_registry)
        self.sub_agent_factory = None  # Will be set by factory
    
    def can_build(self, agent_type: str) -> bool:
        """Check if this builder can handle the agent type"""
        return agent_type in ["llm", "agent"]
    
    def validate_spec(self, spec: AgentSpec) -> bool:
        """Validate LLM agent specification"""
        try:
            agent_spec = spec.spec.get("agent", {})
            
            # Check required fields
            if not agent_spec.get("instruction_template"):
                logger.error("Missing instruction_template")
                return False
            
            # Check model configuration
            model_config = agent_spec.get("model", {})
            if not model_config.get("primary"):
                logger.error("Missing primary model")
                return False
            
            # Validate agent type
            if agent_spec.get("type") not in ["llm", "agent"]:
                logger.error(f"Invalid agent type: {agent_spec.get('type')}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def build(self, spec: AgentSpec, context: AgentContext) -> LlmAgent:
        """Build LLM agent from specification"""
        if not self.validate_spec(spec):
            raise SpecificationError(f"Invalid LLM agent specification: {spec.metadata.get('name')}")
        
        agent_spec = spec.spec.get("agent", {})
        metadata = spec.metadata
        
        # Build instruction inline without separate class
        instruction = self._build_instruction(
            agent_spec["instruction_template"],
            context
        )
        
        # Load tools
        tools = []
        if "tools" in spec.spec:
            tools = self.tool_loader.load_tools(spec.spec["tools"])
        
        # Build sub-agents
        sub_agents = []
        if "sub_agents" in spec.spec and self.sub_agent_factory:
            sub_agents = self._build_sub_agents(spec.spec["sub_agents"], context)
        
        # Get model configuration with fallback support
        model_config = agent_spec.get("model", {})
        model = model_config.get("primary", "gemini-2.0-flash")
        
        # Prepare fallback models
        fallbacks = model_config.get("fallbacks", [])
        
        # Get additional parameters
        parameters = agent_spec.get("parameters", {})
        
        # Include fallback models in parameters if available
        if fallbacks:
            parameters['fallback_models'] = fallbacks
        
        # Create LlmAgent
        try:
            agent = LlmAgent(
                name=metadata.get("name", "unnamed_agent"),
                model=model,
                instruction=instruction,
                description=metadata.get("description", ""),
                tools=tools,
                sub_agents=sub_agents,
                **parameters
            )
            
            logger.info(f"Successfully built LLM agent: {metadata.get('name')}")
            return agent
            
        except Exception as e:
            raise SpecificationError(f"Error creating LLM agent: {e}")
    
    def _build_instruction(self, template: str, context: AgentContext) -> str:
        """Build instruction from template with context variables"""
        if not template:
            raise ValueError("Instruction template cannot be empty")
        
        # Extract variables from template
        variables = self._extract_variables(template)
        
        # Prepare substitution dict
        substitutions = {}
        for var in variables:
            if var in context.variables:
                substitutions[var] = context.variables[var]
            else:
                logger.warning(f"Variable {var} not found in context, using placeholder")
                substitutions[var] = f"[{var}]"
        
        # Perform substitution
        try:
            instruction = Template(template).safe_substitute(**substitutions)
            return instruction.strip()
        except Exception as e:
            raise SpecificationError(f"Error building instruction: {e}")
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template"""
        # Match ${var} and $var patterns
        pattern = r'\$\{?(\w+)\}?'
        matches = re.findall(pattern, template)
        return list(set(matches))
    
    def _build_sub_agents(self, sub_agent_specs: List[Dict], context: AgentContext) -> List:
        """Build sub-agents from specifications"""
        sub_agents = []
        
        for sub_spec in sub_agent_specs:
            # Safer condition evaluation without eval()
            condition = sub_spec.get("condition", "true")
            if not self._evaluate_condition(condition, context):
                continue
            
            # Build sub-agent
            spec_ref = sub_spec.get("spec_ref")
            if spec_ref and self.sub_agent_factory:
                try:
                    sub_context = AgentContext(
                        **context.dict(),
                        parent_agent=context.variables.get("agent_name")
                    )
                    sub_agent = self.sub_agent_factory.build_agent(spec_ref, sub_context)
                    sub_agents.append(sub_agent)
                except Exception as e:
                    logger.error(f"Error building sub-agent {spec_ref}: {e}")
        
        return sub_agents
    
    def _evaluate_condition(self, condition: str, context: AgentContext) -> bool:
        """Evaluate condition expression safely"""
        # Remove eval() for security, use safe evaluation
        if condition == "true":
            return True
        if condition == "false":
            return False
        
        # Safe evaluation of simple conditions
        try:
            # Parse simple attribute access patterns like "input.requires_a"
            if "." in condition:
                parts = condition.split(".")
                if parts[0] == "input" and len(parts) == 2:
                    return context.variables.get(parts[1], False)
            
            # Check if condition is a simple variable name
            if condition in context.variables:
                return bool(context.variables[condition])
            
            # For complex conditions, log warning and default to False
            logger.warning(f"Complex condition '{condition}' not supported, defaulting to False")
            return False
            
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False