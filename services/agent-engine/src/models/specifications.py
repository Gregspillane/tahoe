"""
Pydantic models for all specification types.
Supports agents, workflows, tools, and model configurations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    """Supported agent types in the system."""

    LLM = "llm"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"
    CUSTOM = "custom"


class WorkflowType(str, Enum):
    """Supported workflow types."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class ToolSource(str, Enum):
    """Tool loading sources."""

    REGISTRY = "registry"
    INLINE = "inline"
    IMPORT = "import"


class ModelConfig(BaseModel):
    """Model configuration with fallbacks."""

    primary: str
    fallbacks: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Agent configuration details."""

    type: AgentType
    model: Optional[ModelConfig] = None
    instruction_template: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolReference(BaseModel):
    """Reference to a tool with loading information."""

    name: str
    source: ToolSource = ToolSource.REGISTRY
    definition: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None


class SubAgentReference(BaseModel):
    """Reference to a sub-agent with optional condition."""

    spec_ref: str
    condition: Optional[str] = None


class WorkflowStep(BaseModel):
    """Individual workflow step definition."""

    id: str
    type: Optional[str] = None
    agent_spec: Optional[str] = None
    outputs: Optional[List[str]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    depends_on: Optional[List[str]] = None


class ValidationSchema(BaseModel):
    """Input/output validation schemas."""

    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class SpecMetadata(BaseModel):
    """Common metadata for all specifications."""

    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure names use underscores per ADK requirements."""
        if "-" in v:
            raise ValueError(
                "Names must use underscores, not hyphens (ADK requirement). "
                f"Got: {v}, should be: {v.replace('-', '_')}"
            )
        return v


class AgentSpecification(BaseModel):
    """Complete agent specification."""

    apiVersion: str = Field(default="agent-engine/v1", alias="apiVersion")
    kind: str = Field(default="AgentSpec")
    metadata: SpecMetadata
    spec: Dict[str, Any]

    @field_validator("apiVersion")
    @classmethod
    def validate_api_version(cls, v: str) -> str:
        """Validate API version format."""
        if not v.startswith("agent-engine/"):
            raise ValueError(f"Invalid API version: {v}")
        return v

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: str) -> str:
        """Validate specification kind."""
        valid_kinds = ["AgentSpec", "WorkflowTemplate", "ToolSpec", "ModelConfig"]
        if v not in valid_kinds:
            raise ValueError(f"Invalid kind: {v}. Must be one of {valid_kinds}")
        return v

    class Config:
        populate_by_name = True


class WorkflowTemplate(BaseModel):
    """Complete workflow template specification."""

    apiVersion: str = Field(default="agent-engine/v1", alias="apiVersion")
    kind: str = Field(default="WorkflowTemplate")
    metadata: SpecMetadata
    spec: Dict[str, Any]

    @field_validator("spec")
    @classmethod
    def validate_spec(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow specification structure."""
        if "type" not in v:
            raise ValueError("Workflow spec must include 'type'")
        if "steps" not in v:
            raise ValueError("Workflow spec must include 'steps'")
        return v

    class Config:
        populate_by_name = True


class ToolSpecification(BaseModel):
    """Complete tool specification."""

    apiVersion: str = Field(default="agent-engine/v1", alias="apiVersion")
    kind: str = Field(default="ToolSpec")
    metadata: SpecMetadata
    spec: Dict[str, Any]

    @field_validator("spec")
    @classmethod
    def validate_spec(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool specification structure."""
        if "function_definition" not in v and "description" not in v:
            raise ValueError(
                "Tool spec must include either 'function_definition' or 'description'"
            )
        return v

    class Config:
        populate_by_name = True


class ModelConfiguration(BaseModel):
    """Complete model configuration specification."""

    apiVersion: str = Field(default="agent-engine/v1", alias="apiVersion")
    kind: str = Field(default="ModelConfig")
    metadata: SpecMetadata
    spec: Dict[str, Any]

    @field_validator("spec")
    @classmethod
    def validate_spec(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model configuration structure."""
        if "primary" not in v:
            raise ValueError("Model config must specify 'primary' model")
        return v

    class Config:
        populate_by_name = True


class LoadBalancingConfig(BaseModel):
    """Load balancing configuration for models."""

    strategy: str = "round_robin"
    health_check_interval: int = 30


class ModelFallback(BaseModel):
    """Model fallback configuration."""

    provider: str
    model: str
    trigger_conditions: List[str] = Field(default_factory=list)


class DetailedModelSpec(BaseModel):
    """Detailed model specification within a configuration."""

    provider: str
    model: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class DetailedAgentSpec(BaseModel):
    """Detailed agent specification for parsing."""

    agent: AgentConfig
    tools: List[ToolReference] = Field(default_factory=list)
    sub_agents: List[SubAgentReference] = Field(default_factory=list)
    validation: Optional[ValidationSchema] = None


class DetailedWorkflowSpec(BaseModel):
    """Detailed workflow specification for parsing."""

    type: WorkflowType
    parameters: Optional[Dict[str, Any]] = None
    steps: List[WorkflowStep]


class DetailedToolSpec(BaseModel):
    """Detailed tool specification for parsing."""

    description: str
    function_definition: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class DetailedModelConfigSpec(BaseModel):
    """Detailed model configuration for parsing."""

    primary: DetailedModelSpec
    fallbacks: List[ModelFallback] = Field(default_factory=list)
    load_balancing: Optional[LoadBalancingConfig] = None
