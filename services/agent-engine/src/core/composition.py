"""
Agent composition service with UniversalAgentFactory.
Creates ADK agents from specifications with full compliance.
"""

import re
import importlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# ADK imports - following validated patterns
try:
    from google.genai import types
    from google.genai.chats import Chat
    from google.genai.models import GenerativeModel
    
    # Agent imports
    from google.genai.agents import (
        Agent as LlmAgent,  # LlmAgent is the correct class
        create_agent_executor,
        AgentExecutor
    )
    
    # Try to import workflow agents if available
    try:
        from google.genai.agents import SequentialAgent, ParallelAgent, LoopAgent
        WORKFLOW_AGENTS_AVAILABLE = True
    except ImportError:
        WORKFLOW_AGENTS_AVAILABLE = False
    
    # Tool imports
    from google.genai.tools import FunctionTool, Tool
    
    ADK_AVAILABLE = True
except ImportError:
    # Fallback for development without ADK
    ADK_AVAILABLE = False
    WORKFLOW_AGENTS_AVAILABLE = False
    
    # Mock classes for development
    class LlmAgent:
        def __init__(self, name, model, instruction, description="", tools=None, **kwargs):
            self.name = name
            self.model = model
            self.instruction = instruction
            self.description = description
            self.tools = tools or []
    
    class FunctionTool:
        def __init__(self, func):
            self.func = func

from .specifications import SpecificationParser, SpecificationValidator


class UniversalAgentFactory:
    """Factory for creating any agent type from specifications."""
    
    def __init__(self):
        """Initialize the factory."""
        self.parser = SpecificationParser()
        self.validator = SpecificationValidator()
        self.tool_registry = {}  # Will be populated from tool registry service
        self._compiled_functions = {}  # Cache for compiled inline functions
    
    def build_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Build any agent type from specification."""
        # Sanitize names before validation
        if "metadata" in spec and "name" in spec["metadata"]:
            original_name = spec["metadata"]["name"]
            sanitized_name = self._sanitize_name(original_name)
            if original_name != sanitized_name:
                # Create a copy with sanitized name for validation
                spec = dict(spec)
                spec["metadata"] = dict(spec["metadata"])
                spec["metadata"]["name"] = sanitized_name
        
        # Validate specification
        self.validator.validate_agent_spec(spec)
        
        agent_type = spec["spec"]["agent"]["type"]
        
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
            raise ValueError(f"Unsupported agent type: {agent_type}")
    
    def _build_llm_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> LlmAgent:
        """Build LLM agent with dynamic configuration."""
        agent_spec = spec["spec"]["agent"]
        metadata = spec["metadata"]
        
        # Ensure name uses underscores (ADK requirement)
        agent_name = self._sanitize_name(metadata["name"])
        
        # Load tools
        tools = self._load_tools(spec["spec"].get("tools", []))
        
        # Build instruction from template
        instruction = self._build_instruction(
            agent_spec.get("instruction_template", ""),
            context
        )
        
        # Get model configuration
        model_config = agent_spec.get("model", {})
        model_name = model_config.get("primary", "gemini-2.0-flash")
        
        # Extract additional parameters
        params = agent_spec.get("parameters", {})
        
        # Create LLM agent
        if ADK_AVAILABLE:
            agent = LlmAgent(
                name=agent_name,
                model=model_name,
                instruction=instruction,
                description=metadata.get("description", ""),
                tools=tools,
                **params
            )
        else:
            # Mock for development
            agent = LlmAgent(
                name=agent_name,
                model=model_name,
                instruction=instruction,
                description=metadata.get("description", ""),
                tools=tools
            )
        
        # Handle sub-agents if specified
        sub_agents = spec["spec"].get("sub_agents", [])
        if sub_agents:
            # In real ADK, sub_agents would be added to the agent
            # For now, store them as an attribute
            agent._sub_agents = self._build_sub_agents(sub_agents, context)
        
        return agent
    
    def _build_sequential_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Build sequential workflow agent."""
        if not WORKFLOW_AGENTS_AVAILABLE:
            return self._build_mock_workflow_agent(spec, context, "sequential")
        
        metadata = spec["metadata"]
        agent_name = self._sanitize_name(metadata["name"])
        
        # Build sub-agents
        sub_agents = self._build_sub_agents(spec["spec"].get("sub_agents", []), context)
        
        return SequentialAgent(
            name=agent_name,
            sub_agents=sub_agents,
            description=metadata.get("description", "")
        )
    
    def _build_parallel_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Build parallel workflow agent."""
        if not WORKFLOW_AGENTS_AVAILABLE:
            return self._build_mock_workflow_agent(spec, context, "parallel")
        
        metadata = spec["metadata"]
        agent_name = self._sanitize_name(metadata["name"])
        
        # Build sub-agents
        sub_agents = self._build_sub_agents(spec["spec"].get("sub_agents", []), context)
        
        return ParallelAgent(
            name=agent_name,
            sub_agents=sub_agents,
            description=metadata.get("description", "")
        )
    
    def _build_loop_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Build loop agent following ADK patterns."""
        if not WORKFLOW_AGENTS_AVAILABLE:
            return self._build_mock_workflow_agent(spec, context, "loop")
        
        metadata = spec["metadata"]
        agent_name = self._sanitize_name(metadata["name"])
        
        # Build sub-agents - LoopAgent takes a list per ADK requirements
        sub_agents = self._build_sub_agents(spec["spec"].get("sub_agents", []), context)
        
        return LoopAgent(
            name=agent_name,
            sub_agents=sub_agents,  # List, not single agent
            description=metadata.get("description", "")
        )
    
    def _build_custom_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """Build custom agent implementation."""
        # Custom agents would extend BaseAgent
        # For now, return a mock
        metadata = spec["metadata"]
        agent_name = self._sanitize_name(metadata["name"])
        
        class CustomAgent:
            def __init__(self):
                self.name = agent_name
                self.description = metadata.get("description", "")
                self.spec = spec
        
        return CustomAgent()
    
    def _build_mock_workflow_agent(self, spec: Dict[str, Any], context: Optional[Dict[str, Any]], agent_type: str) -> Any:
        """Build mock workflow agent for development."""
        metadata = spec["metadata"]
        agent_name = self._sanitize_name(metadata["name"])
        
        class MockWorkflowAgent:
            def __init__(self):
                self.name = agent_name
                self.type = agent_type
                self.description = metadata.get("description", "")
                self.sub_agents = self._build_sub_agents(spec["spec"].get("sub_agents", []), context)
        
        return MockWorkflowAgent()
    
    def _sanitize_name(self, name: str) -> str:
        """Ensure name uses underscores per ADK requirements."""
        return name.replace("-", "_")
    
    def _load_tools(self, tool_refs: List[Dict[str, Any]]) -> List:
        """Load tools from references."""
        tools = []
        
        for tool_ref in tool_refs:
            source = tool_ref.get("source", "registry")
            
            if source == "registry":
                # Load from tool registry
                tool_name = tool_ref["name"]
                if tool_name in self.tool_registry:
                    tools.append(self.tool_registry[tool_name])
                else:
                    # Try to load built-in tools
                    if tool_name == "google_search" and ADK_AVAILABLE:
                        try:
                            from google.genai.tools import google_search
                            tools.append(google_search)
                        except ImportError:
                            pass
            
            elif source == "inline":
                # Create function from inline definition
                tool_func = self._compile_inline_function(tool_ref)
                if tool_func:
                    tools.append(tool_func)
            
            elif source == "import":
                # Import from module
                tool_func = self._import_tool_function(tool_ref)
                if tool_func:
                    tools.append(tool_func)
        
        return tools
    
    def _compile_inline_function(self, tool_ref: Dict[str, Any]) -> Optional[callable]:
        """Compile and return inline function definition."""
        definition = tool_ref.get("definition", "")
        if not definition:
            return None
        
        # Extract function name
        match = re.search(r'def\s+(\w+)\s*\(', definition)
        if not match:
            return None
        
        func_name = match.group(1)
        
        # Check cache
        cache_key = f"{func_name}_{hash(definition)}"
        if cache_key in self._compiled_functions:
            return self._compiled_functions[cache_key]
        
        try:
            # Compile the function
            namespace = {}
            exec(definition, namespace)
            
            if func_name in namespace:
                func = namespace[func_name]
                self._compiled_functions[cache_key] = func
                return func
        except Exception as e:
            print(f"Failed to compile inline function {func_name}: {e}")
        
        return None
    
    def _import_tool_function(self, tool_ref: Dict[str, Any]) -> Optional[callable]:
        """Import tool function from module."""
        module_name = tool_ref.get("module")
        function_name = tool_ref.get("function", tool_ref.get("name"))
        
        if not module_name or not function_name:
            return None
        
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                return getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            print(f"Failed to import {function_name} from {module_name}: {e}")
        
        return None
    
    def _build_sub_agents(self, sub_agent_refs: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List:
        """Build sub-agents from references."""
        sub_agents = []
        
        for ref in sub_agent_refs:
            # Check condition if present
            if "condition" in ref:
                if not self._evaluate_condition(ref["condition"], context):
                    continue
            
            # Load and build sub-agent specification
            spec_ref = ref["spec_ref"]
            try:
                sub_spec = self.parser.load_agent_spec(spec_ref)
                sub_agent = self.build_agent(sub_spec, context)
                sub_agents.append(sub_agent)
            except Exception as e:
                print(f"Failed to build sub-agent {spec_ref}: {e}")
        
        return sub_agents
    
    def _build_instruction(self, template: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build instruction from template with context."""
        if not context or not template:
            return template
        
        instruction = template
        
        # Simple template substitution
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in instruction:
                instruction = instruction.replace(placeholder, str(value))
        
        return instruction
    
    def _evaluate_condition(self, condition: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate condition expression safely."""
        if condition == "true":
            return True
        if condition == "false":
            return False
        
        if not context:
            return False
        
        # Safe evaluation with limited context
        try:
            # Only allow simple comparisons and boolean operations
            safe_globals = {
                "__builtins__": {},
                "True": True,
                "False": False,
                "None": None
            }
            safe_context = {**safe_globals, **context}
            return eval(condition, safe_context)
        except Exception:
            return False


class AgentCompositionService:
    """Service to compose agents from specifications."""
    
    def __init__(self, tool_registry: Optional[Dict[str, Any]] = None):
        """Initialize composition service."""
        self.parser = SpecificationParser()
        self.validator = SpecificationValidator()
        self.factory = UniversalAgentFactory()
        
        # Set tool registry if provided
        if tool_registry:
            self.factory.tool_registry = tool_registry
    
    def build_agent_from_spec(self, spec_name: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Build agent from specification name."""
        # Load specification
        spec = self.parser.load_agent_spec(spec_name)
        
        # Validate specification
        self.validator.validate_agent_spec(spec)
        
        # Check for ADK compliance warnings
        warnings = self.validator.check_adk_compliance(spec)
        if warnings:
            for warning in warnings:
                print(f"ADK Compliance Warning: {warning}")
        
        # Build agent using factory
        return self.factory.build_agent(spec, context)
    
    def build_workflow_from_template(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Build workflow from template specification."""
        # Load workflow template
        template = self.parser.load_workflow_template(template_name)
        
        # Validate workflow
        self.validator.validate_workflow_spec(template)
        
        # Convert workflow to agent specification
        agent_spec = self._workflow_to_agent_spec(template)
        
        # Build using factory
        return self.factory.build_agent(agent_spec, context)
    
    def _workflow_to_agent_spec(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Convert workflow template to agent specification."""
        workflow_type = workflow["spec"]["type"]
        
        # Map workflow type to agent type
        agent_type_map = {
            "sequential": "sequential",
            "parallel": "parallel",
            "loop": "loop",
            "conditional": "sequential"  # Conditional workflows use sequential with logic
        }
        
        agent_spec = {
            "apiVersion": workflow["apiVersion"],
            "kind": "AgentSpec",
            "metadata": workflow["metadata"],
            "spec": {
                "agent": {
                    "type": agent_type_map.get(workflow_type, "sequential")
                },
                "sub_agents": []
            }
        }
        
        # Convert workflow steps to sub-agents
        for step in workflow["spec"].get("steps", []):
            if "agent_spec" in step:
                agent_spec["spec"]["sub_agents"].append({
                    "spec_ref": step["agent_spec"],
                    "condition": step.get("condition", "true")
                })
        
        return agent_spec
    
    def list_available_agents(self) -> List[str]:
        """List all available agent specifications."""
        return self.parser.list_specifications("agents")
    
    def list_available_workflows(self) -> List[str]:
        """List all available workflow templates."""
        return self.parser.list_specifications("workflows")
    
    def list_available_tools(self) -> List[str]:
        """List all available tool specifications."""
        return self.parser.list_specifications("tools")
    
    def list_available_models(self) -> List[str]:
        """List all available model configurations."""
        return self.parser.list_specifications("models")
    
    def validate_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specification and return results."""
        kind = spec.get("kind")
        
        try:
            if kind == "AgentSpec":
                self.validator.validate_agent_spec(spec)
            elif kind == "WorkflowTemplate":
                self.validator.validate_workflow_spec(spec)
            elif kind == "ToolSpec":
                self.validator.validate_tool_spec(spec)
            elif kind == "ModelConfig":
                self.validator.validate_model_spec(spec)
            else:
                return {"valid": False, "error": f"Unknown kind: {kind}"}
            
            # Check for ADK compliance warnings
            warnings = self.validator.check_adk_compliance(spec)
            
            return {
                "valid": True,
                "kind": kind,
                "warnings": warnings
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "kind": kind
            }