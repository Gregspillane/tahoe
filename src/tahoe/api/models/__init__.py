"""
API request and response models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class AgentType(str, Enum):
    """Supported agent types in Tahoe"""
    LLM = "llm"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LOOP = "loop"
    CUSTOM = "custom"


class AgentCreateRequest(BaseModel):
    """Request to create a new agent instance"""
    name: str = Field(..., description="Unique name for the agent")
    type: AgentType = Field(..., description="Type of agent to create")
    config: Dict[str, Any] = Field(..., description="Agent configuration (model, tools, etc.)")
    description: Optional[str] = Field(None, description="Agent description")
    template: Optional[str] = Field(None, description="Template name to use")


class AgentExecuteRequest(BaseModel):
    """Request to execute an agent"""
    agent_id: str = Field(..., description="ID of the agent to execute")
    input: str = Field(..., description="Input message/query for the agent")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class AgentResponse(BaseModel):
    """Response from agent execution"""
    agent_id: str
    session_id: str
    response: str
    state: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    user_id: str = Field(..., description="User/client identifier")
    agent_id: str = Field(..., description="Agent to associate with session")
    initial_state: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial state")


class SessionResponse(BaseModel):
    """Session information response"""
    session_id: str
    user_id: str
    agent_id: str
    state: Dict[str, Any]
    created_at: str
    last_updated: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None