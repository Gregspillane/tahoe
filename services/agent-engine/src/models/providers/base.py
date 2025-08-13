"""Base provider interface for LLM implementations"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider"""
    content: str
    model_used: str
    usage: Dict[str, int]  # tokens used, etc.
    raw_response: Any  # Original provider response
    metadata: Dict[str, Any] = None


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class BaseProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._client = None
        self.provider_type: ProviderType = None
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider client"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> ProviderResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def check_availability(self, model: str) -> bool:
        """Check if a specific model is available"""
        pass
    
    @abstractmethod
    def list_available_models(self) -> List[str]:
        """List all available models for this provider"""
        pass
    
    @abstractmethod
    async def validate_api_key(self) -> bool:
        """Validate the API key is working"""
        pass
    
    def format_messages(self, prompt: str, system_prompt: str = None) -> List[Dict[str, str]]:
        """Format messages for chat-based models"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages
    
    async def close(self) -> None:
        """Cleanup provider resources"""
        if hasattr(self._client, 'close'):
            await self._client.close()
        self._client = None