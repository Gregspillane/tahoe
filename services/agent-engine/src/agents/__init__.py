"""Agent module for Project Tahoe.

Provides agent factory and base classes for multi-agent orchestration.
"""

from .factory import AgentFactory
from .base import BaseSpecialistAgent, AgentResult

__all__ = ['AgentFactory', 'BaseSpecialistAgent', 'AgentResult']
