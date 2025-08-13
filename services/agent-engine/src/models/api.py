"""API Request and Response Models for agent-engine"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


# Request Models
class InteractionData(BaseModel):
    """Interaction data for analysis"""
    id: str
    type: str = Field(..., description="call, email, chat, etc.")
    content: str = Field(..., description="transcript, email body, etc.")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalysisRequest(BaseModel):
    """Request to analyze an interaction"""
    interaction: InteractionData
    scorecard_id: str = Field(..., description="ID of the scorecard to use")
    portfolio_id: str = Field(..., description="Portfolio context ID")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentTemplateCreate(BaseModel):
    """Create a new agent template"""
    name: str
    description: Optional[str] = None
    type: str = Field(..., description="specialist, coordinator, or aggregator")
    model: str = Field(default="gemini-2.0-flash")
    modelConfig: Dict[str, Any] = Field(default_factory=dict)
    capabilities: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    triggerRules: Dict[str, Any] = Field(default_factory=dict)
    systemPrompt: Optional[str] = None
    userPrompt: Optional[str] = None


class AgentTemplateUpdate(BaseModel):
    """Update an agent template"""
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    modelConfig: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    triggerRules: Optional[Dict[str, Any]] = None
    systemPrompt: Optional[str] = None
    userPrompt: Optional[str] = None
    isActive: Optional[bool] = None


class ScorecardCreate(BaseModel):
    """Create a new scorecard"""
    name: str
    description: Optional[str] = None
    portfolioId: str
    requirements: Dict[str, Any] = Field(default_factory=dict)
    thresholds: Dict[str, Any] = Field(default_factory=dict)
    aggregationRules: Dict[str, Any] = Field(default_factory=dict)


# Response Models
class AnalysisResponse(BaseModel):
    """Response from analysis endpoint"""
    analysis_id: str
    status: str
    overall_score: Optional[float] = None
    confidence: Optional[float] = None
    categories: Optional[Dict[str, Any]] = None
    violations: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    audit_trail: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None


class AnalysisStatus(BaseModel):
    """Real-time analysis status"""
    analysis_id: str
    status: str
    phase: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    trace_id: Optional[str] = None


class HealthStatus(BaseModel):
    """Service health status"""
    service: str
    status: str
    version: str
    dependencies: Dict[str, str]
    timestamp: str


class MetricsResponse(BaseModel):
    """Service metrics"""
    requests_total: int
    requests_per_minute: float
    average_response_time: float
    active_analyses: int
    cache_hit_rate: float
    errors_total: int
    timestamp: str


# Internal Models
class AnalysisResult(BaseModel):
    """Internal analysis result model"""
    analysis_id: str
    overall_score: float
    confidence: float
    categories: Dict[str, Any]
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    execution_time: float
    audit_trail: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return self.model_dump()


class AuthContext(BaseModel):
    """Authentication context"""
    token: str
    service_name: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)