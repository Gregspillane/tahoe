"""Base classes for Tahoe specialist agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
import time


@dataclass
class AgentResult:
    """Standardized agent result format."""
    agent_name: str
    agent_version: str
    score: float  # 0-100
    confidence: float  # 0-1
    findings: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    execution_time: float
    metadata: Dict[str, Any]


class BaseSpecialistAgent(ABC):
    """Base class for all specialist agents."""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        
    @abstractmethod
    async def analyze(self, interaction: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """Perform specialized analysis on the interaction."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides."""
        pass
    
    def _measure_execution_time(self, func):
        """Decorator to measure execution time."""
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            if hasattr(result, 'execution_time'):
                result.execution_time = execution_time
            return result
        return wrapper