"""
API endpoints for specification management.
Provides CRUD operations for all specification types.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ..core.specifications import SpecificationParser, SpecificationValidator
from ..core.composition import AgentCompositionService
from ..services.configuration_version import ConfigurationVersionService


# Request/Response models
class SpecValidationRequest(BaseModel):
    """Request model for specification validation."""

    specification: Dict[str, Any]


class SpecValidationResponse(BaseModel):
    """Response model for specification validation."""

    valid: bool
    kind: Optional[str] = None
    error: Optional[str] = None
    warnings: List[str] = []


class AgentComposeRequest(BaseModel):
    """Request model for agent composition."""

    spec_name: str
    context: Optional[Dict[str, Any]] = None


class AgentComposeResponse(BaseModel):
    """Response model for agent composition."""

    agent_id: str
    agent_name: str
    agent_type: str
    message: str


class SpecListResponse(BaseModel):
    """Response model for listing specifications."""

    specifications: List[str]
    count: int


class VersionHistoryResponse(BaseModel):
    """Response model for version history."""

    versions: List[Dict[str, Any]]
    current_version: Optional[str] = None


# Create router
router = APIRouter(prefix="/specs", tags=["specifications"])

# Initialize services
parser = SpecificationParser()
validator = SpecificationValidator()
composition_service = AgentCompositionService()
version_service = ConfigurationVersionService()


@router.post("/validate", response_model=SpecValidationResponse)
async def validate_specification(request: SpecValidationRequest):
    """
    Validate a specification against schema and ADK requirements.

    Validates any specification type (AgentSpec, WorkflowTemplate, ToolSpec, ModelConfig)
    and checks for ADK compliance issues.
    """
    try:
        result = composition_service.validate_specification(request.specification)
        return SpecValidationResponse(**result)
    except Exception as e:
        return SpecValidationResponse(valid=False, error=str(e))


@router.get("/agents", response_model=SpecListResponse)
async def list_agent_specifications():
    """
    List all available agent specifications.

    Returns a list of agent specification names that can be used
    for composition.
    """
    try:
        agents = parser.list_specifications("agents")
        return SpecListResponse(specifications=agents, count=len(agents))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{spec_name}")
async def get_agent_specification(spec_name: str):
    """
    Get a specific agent specification by name.

    Returns the full agent specification including metadata and spec details.
    """
    try:
        spec = parser.load_agent_spec(spec_name)
        # Track version
        checksum = version_service.track_specification_version(spec)
        spec["_version"] = checksum[:8]
        return spec
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Agent specification '{spec_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows", response_model=SpecListResponse)
async def list_workflow_templates():
    """
    List all available workflow templates.

    Returns a list of workflow template names.
    """
    try:
        workflows = parser.list_specifications("workflows")
        return SpecListResponse(specifications=workflows, count=len(workflows))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{template_name}")
async def get_workflow_template(template_name: str):
    """
    Get a specific workflow template by name.

    Returns the full workflow template specification.
    """
    try:
        spec = parser.load_workflow_template(template_name)
        # Track version
        checksum = version_service.track_specification_version(spec)
        spec["_version"] = checksum[:8]
        return spec
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Workflow template '{template_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", response_model=SpecListResponse)
async def list_tool_specifications():
    """
    List all available tool specifications.

    Returns a list of tool specification names.
    """
    try:
        tools = parser.list_specifications("tools")
        return SpecListResponse(specifications=tools, count=len(tools))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/{tool_name}")
async def get_tool_specification(tool_name: str):
    """
    Get a specific tool specification by name.

    Returns the full tool specification including function definition.
    """
    try:
        spec = parser.load_tool_spec(tool_name)
        # Track version
        checksum = version_service.track_specification_version(spec)
        spec["_version"] = checksum[:8]
        return spec
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Tool specification '{tool_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=SpecListResponse)
async def list_model_configurations():
    """
    List all available model configurations.

    Returns a list of model configuration names.
    """
    try:
        models = parser.list_specifications("models")
        return SpecListResponse(specifications=models, count=len(models))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{config_name}")
async def get_model_configuration(config_name: str):
    """
    Get a specific model configuration by name.

    Returns the full model configuration including fallback strategies.
    """
    try:
        spec = parser.load_model_config(config_name)
        # Track version
        checksum = version_service.track_specification_version(spec)
        spec["_version"] = checksum[:8]
        return spec
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Model configuration '{config_name}' not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/compose", response_model=AgentComposeResponse)
async def compose_agent(request: AgentComposeRequest):
    """
    Compose an agent from a specification.

    Creates an ADK agent instance from the specified agent specification
    with optional context for template variables.
    """
    try:
        # Build agent from specification
        agent = composition_service.build_agent_from_spec(
            request.spec_name, request.context
        )

        # Generate agent ID (in production, this would be stored)
        import uuid

        agent_id = str(uuid.uuid4())[:8]

        return AgentComposeResponse(
            agent_id=agent_id,
            agent_name=agent.name if hasattr(agent, "name") else request.spec_name,
            agent_type=type(agent).__name__,
            message=f"Agent successfully composed from specification '{request.spec_name}'",
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Agent specification '{request.spec_name}' not found",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/compose")
async def compose_workflow(
    template_name: str = Body(...), context: Optional[Dict[str, Any]] = Body(None)
):
    """
    Compose a workflow from a template.

    Creates a workflow agent from the specified template.
    """
    try:
        # Build workflow from template
        workflow = composition_service.build_workflow_from_template(
            template_name, context
        )

        # Generate workflow ID
        import uuid

        workflow_id = str(uuid.uuid4())[:8]

        return {
            "workflow_id": workflow_id,
            "template_name": template_name,
            "workflow_type": type(workflow).__name__,
            "message": f"Workflow successfully composed from template '{template_name}'",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Workflow template '{template_name}' not found"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/versions/{kind}/{name}", response_model=VersionHistoryResponse)
async def get_specification_versions(kind: str, name: str):
    """
    Get version history for a specification.

    Returns all tracked versions of the specified specification.
    """
    try:
        history = version_service.get_specification_history(kind, name)
        latest = version_service.get_latest_version(kind, name)

        return VersionHistoryResponse(
            versions=history,
            current_version=latest.get("metadata", {}).get("version")
            if latest
            else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/versions/rollback")
async def rollback_specification(
    kind: str = Body(...), name: str = Body(...), checksum: str = Body(...)
):
    """
    Rollback to a specific version of a specification.

    Restores a previous version of a specification by its checksum.
    """
    try:
        spec = version_service.rollback_to_version(kind, name, checksum)
        if spec:
            return {
                "success": True,
                "message": f"Successfully rolled back to version {checksum[:8]}",
                "specification": spec,
            }
        else:
            raise HTTPException(status_code=404, detail="Version not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_specification_statistics():
    """
    Get statistics about specifications and versions.

    Returns counts and breakdown of all tracked specifications.
    """
    try:
        stats = version_service.get_statistics()

        # Add current specification counts
        stats["current_specifications"] = {
            "agents": len(parser.list_specifications("agents")),
            "workflows": len(parser.list_specifications("workflows")),
            "tools": len(parser.list_specifications("tools")),
            "models": len(parser.list_specifications("models")),
        }

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_specifications():
    """
    Reload all specifications from disk.

    Clears the cache and reloads all specifications.
    """
    try:
        # Clear parser cache
        parser.loaded_specs.clear()

        # Reload and count specifications
        counts = {
            "agents": len(parser.list_specifications("agents")),
            "workflows": len(parser.list_specifications("workflows")),
            "tools": len(parser.list_specifications("tools")),
            "models": len(parser.list_specifications("models")),
        }

        return {
            "success": True,
            "message": "Specifications reloaded successfully",
            "counts": counts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
