"""
Specification parser and validator with ADK compliance.
Handles YAML/JSON specifications for agents, workflows, tools, and models.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List

from ..models.specifications import (
    AgentSpecification,
    WorkflowTemplate,
    ToolSpecification,
    ModelConfiguration,
)


class SpecificationParser:
    """Parse and load specifications from YAML/JSON files."""

    def __init__(self, base_path: str = "specs"):
        """Initialize parser with base path for specifications."""
        self.base_path = Path(base_path)
        self.loaded_specs: Dict[str, Dict[str, Any]] = {}
        self._ensure_base_path()

    def _ensure_base_path(self):
        """Ensure base path exists."""
        if not self.base_path.exists():
            # Try relative to agent-engine service
            service_path = Path(__file__).parent.parent.parent
            self.base_path = service_path / "specs"
            if not self.base_path.exists():
                self.base_path.mkdir(parents=True, exist_ok=True)

    def load_spec(self, spec_path: str, force_reload: bool = False) -> Dict[str, Any]:
        """Load specification from file with caching."""
        if not force_reload and spec_path in self.loaded_specs:
            return self.loaded_specs[spec_path].copy()

        full_path = self._resolve_path(spec_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Specification not found: {full_path}")

        # Load based on file extension
        if full_path.suffix in [".yaml", ".yml"]:
            spec = self._load_yaml(full_path)
        elif full_path.suffix == ".json":
            spec = self._load_json(full_path)
        else:
            raise ValueError(f"Unsupported file format: {full_path.suffix}")

        # Resolve references and cache
        spec = self.resolve_references(spec)
        self.loaded_specs[spec_path] = spec

        return spec.copy()

    def _resolve_path(self, spec_path: str) -> Path:
        """Resolve specification path."""
        path = Path(spec_path)
        if path.is_absolute():
            return path
        return self.base_path / path

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML specification."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON specification."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}")

    def resolve_references(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve $ref references in specification."""
        if "$ref" in spec:
            ref_path = spec["$ref"]
            referenced = self.load_spec(ref_path)
            # Merge referenced spec with current, current values override
            merged = referenced.copy()
            merged.update({k: v for k, v in spec.items() if k != "$ref"})
            spec = merged

        # Recursively resolve nested references
        for key, value in spec.items():
            if isinstance(value, dict):
                spec[key] = self.resolve_references(value)
            elif isinstance(value, list):
                spec[key] = [
                    self.resolve_references(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return spec

    def load_agent_spec(self, spec_name: str) -> Dict[str, Any]:
        """Load agent specification by name."""
        # Try with and without .yaml extension
        for ext in ["", ".yaml", ".yml", ".json"]:
            spec_path = f"agents/{spec_name}{ext}"
            try:
                return self.load_spec(spec_path)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Agent specification not found: {spec_name}")

    def load_workflow_template(self, template_name: str) -> Dict[str, Any]:
        """Load workflow template by name."""
        for ext in ["", ".yaml", ".yml", ".json"]:
            spec_path = f"workflows/{template_name}{ext}"
            try:
                return self.load_spec(spec_path)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Workflow template not found: {template_name}")

    def load_tool_spec(self, tool_name: str) -> Dict[str, Any]:
        """Load tool specification by name."""
        for ext in ["", ".yaml", ".yml", ".json"]:
            spec_path = f"tools/{tool_name}{ext}"
            try:
                return self.load_spec(spec_path)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Tool specification not found: {tool_name}")

    def load_model_config(self, config_name: str) -> Dict[str, Any]:
        """Load model configuration by name."""
        for ext in ["", ".yaml", ".yml", ".json"]:
            spec_path = f"models/{config_name}{ext}"
            try:
                return self.load_spec(spec_path)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"Model configuration not found: {config_name}")

    def list_specifications(self, spec_type: str) -> List[str]:
        """List all specifications of a given type."""
        type_dir = self.base_path / spec_type
        if not type_dir.exists():
            return []

        specs = []
        for file_path in type_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".yaml", ".yml", ".json"]:
                # Get relative path without extension
                rel_path = file_path.relative_to(type_dir)
                spec_name = str(rel_path.with_suffix(""))
                specs.append(spec_name)

        return sorted(specs)


class SpecificationValidator:
    """Validate specifications against schemas and ADK requirements."""

    def __init__(self):
        """Initialize validator with schemas."""
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._load_schemas()

    def _load_schemas(self):
        """Load JSON schemas for validation."""
        # For now, we'll use basic validation via Pydantic models
        # In production, load actual JSON schemas from files
        self.schemas = {
            "AgentSpec": {
                "type": "object",
                "required": ["apiVersion", "kind", "metadata", "spec"],
            },
            "WorkflowTemplate": {
                "type": "object",
                "required": ["apiVersion", "kind", "metadata", "spec"],
            },
            "ToolSpec": {
                "type": "object",
                "required": ["apiVersion", "kind", "metadata", "spec"],
            },
            "ModelConfig": {
                "type": "object",
                "required": ["apiVersion", "kind", "metadata", "spec"],
            },
        }

    def validate_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate specification against schema."""
        kind = spec.get("kind")
        if not kind:
            raise ValueError("Missing 'kind' field in specification")

        # Use Pydantic models for validation
        try:
            if kind == "AgentSpec":
                AgentSpecification(**spec)
            elif kind == "WorkflowTemplate":
                WorkflowTemplate(**spec)
            elif kind == "ToolSpec":
                ToolSpecification(**spec)
            elif kind == "ModelConfig":
                ModelConfiguration(**spec)
            else:
                raise ValueError(f"Unknown specification kind: {kind}")
            return True
        except Exception as e:
            raise ValueError(f"Specification validation failed: {e}")

    def validate_agent_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate agent specification with ADK compliance checks."""
        # Basic validation
        self.validate_spec(spec)

        # Check agent name for ADK compliance (underscores only)
        agent_name = spec.get("metadata", {}).get("name", "")
        if "-" in agent_name:
            raise ValueError(
                f"Agent names must use underscores, not hyphens (ADK requirement). "
                f"Got: {agent_name}, should be: {agent_name.replace('-', '_')}"
            )

        # Validate agent type specific requirements
        agent_spec = spec.get("spec", {})
        agent_config = agent_spec.get("agent", {})
        agent_type = agent_config.get("type")

        if agent_type == "llm":
            self._validate_llm_agent(agent_config)
        elif agent_type in ["sequential", "parallel"]:
            self._validate_workflow_agent(agent_config, agent_spec)
        elif agent_type == "loop":
            self._validate_loop_agent(agent_config, agent_spec)
        elif agent_type == "custom":
            pass  # Custom agents have flexible validation
        else:
            raise ValueError(f"Invalid agent type: {agent_type}")

        return True

    def _validate_llm_agent(self, agent_config: Dict[str, Any]):
        """Validate LLM agent configuration."""
        required = ["model", "instruction_template"]
        for field in required:
            if field not in agent_config:
                raise ValueError(f"Missing required field for LLM agent: {field}")

        # Validate model configuration
        model = agent_config["model"]
        if not isinstance(model, dict) or "primary" not in model:
            raise ValueError("LLM agent must specify primary model")

    def _validate_workflow_agent(
        self, agent_config: Dict[str, Any], agent_spec: Dict[str, Any]
    ):
        """Validate workflow agent configuration."""
        # Workflow agents need sub_agents
        if "sub_agents" not in agent_spec:
            raise ValueError("Workflow agents require 'sub_agents' field")

        sub_agents = agent_spec["sub_agents"]
        if not isinstance(sub_agents, list) or len(sub_agents) == 0:
            raise ValueError("Workflow agents must have at least one sub-agent")

    def _validate_loop_agent(
        self, agent_config: Dict[str, Any], agent_spec: Dict[str, Any]
    ):
        """Validate loop agent configuration per ADK requirements."""
        # Per ADK patterns, LoopAgent uses sub_agents as list
        if "sub_agents" not in agent_spec:
            raise ValueError("LoopAgent requires 'sub_agents' parameter")

        sub_agents = agent_spec["sub_agents"]
        if not isinstance(sub_agents, list):
            raise ValueError("LoopAgent 'sub_agents' must be a list (ADK requirement)")

        if len(sub_agents) == 0:
            raise ValueError("LoopAgent must have at least one sub-agent")

    def validate_workflow_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate workflow specification."""
        self.validate_spec(spec)

        workflow_spec = spec.get("spec", {})

        # Check workflow type
        workflow_type = workflow_spec.get("type")
        if workflow_type not in ["sequential", "parallel", "conditional", "loop"]:
            raise ValueError(f"Invalid workflow type: {workflow_type}")

        # Validate steps
        steps = workflow_spec.get("steps", [])
        if not steps:
            raise ValueError("Workflow must have at least one step")

        # Validate each step
        step_ids = set()
        for step in steps:
            if not isinstance(step, dict) or "id" not in step:
                raise ValueError("Each workflow step must have an 'id'")

            step_id = step["id"]
            if step_id in step_ids:
                raise ValueError(f"Duplicate step id: {step_id}")
            step_ids.add(step_id)

            # Check dependencies exist
            if "depends_on" in step:
                for dep in step["depends_on"]:
                    if dep not in step_ids:
                        raise ValueError(
                            f"Step {step_id} depends on unknown step: {dep}"
                        )

        return True

    def validate_tool_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate tool specification."""
        self.validate_spec(spec)

        tool_spec = spec.get("spec", {})

        # Check required fields
        if "description" not in tool_spec:
            raise ValueError("Tool spec must include 'description'")

        # If function_definition exists, validate it's a string
        if "function_definition" in tool_spec:
            if not isinstance(tool_spec["function_definition"], str):
                raise ValueError("Tool function_definition must be a string")

        # Validate dependencies and categories
        if "dependencies" in tool_spec:
            if not isinstance(tool_spec["dependencies"], list):
                raise ValueError("Tool dependencies must be a list")

        if "categories" in tool_spec:
            if not isinstance(tool_spec["categories"], list):
                raise ValueError("Tool categories must be a list")

        return True

    def validate_model_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate model configuration."""
        self.validate_spec(spec)

        model_spec = spec.get("spec", {})

        # Check primary model
        if "primary" not in model_spec:
            raise ValueError("Model config must specify 'primary' model")

        primary = model_spec["primary"]
        if not isinstance(primary, dict):
            raise ValueError("Primary model must be a configuration object")

        if "model" not in primary:
            raise ValueError("Primary model config must specify 'model' name")

        # Validate fallbacks if present
        if "fallbacks" in model_spec:
            fallbacks = model_spec["fallbacks"]
            if not isinstance(fallbacks, list):
                raise ValueError("Model fallbacks must be a list")

            for i, fallback in enumerate(fallbacks):
                if not isinstance(fallback, dict) or "model" not in fallback:
                    raise ValueError(f"Fallback {i} must specify 'model'")

        return True

    def check_adk_compliance(self, spec: Dict[str, Any]) -> List[str]:
        """Check specification for ADK anti-patterns and return warnings."""
        warnings = []
        kind = spec.get("kind")

        if kind == "AgentSpec":
            metadata = spec.get("metadata", {})
            name = metadata.get("name", "")

            # Check naming convention
            if "-" in name:
                warnings.append(
                    f"Agent name '{name}' uses hyphens. ADK requires underscores. "
                    f"Should be: {name.replace('-', '_')}"
                )

            # Check for common anti-patterns
            agent_spec = spec.get("spec", {})
            agent_config = agent_spec.get("agent", {})

            # Check if trying to set model at creation time
            if "parameters" in agent_config:
                params = agent_config["parameters"]
                if "model" in params:
                    warnings.append(
                        "Model should not be set in agent parameters. "
                        "Use model configuration section instead."
                    )

            # Check loop agent structure
            if agent_config.get("type") == "loop":
                if "sub_agent" in agent_spec:
                    warnings.append(
                        "LoopAgent should use 'sub_agents' (list) not 'sub_agent' (single)"
                    )

        return warnings
