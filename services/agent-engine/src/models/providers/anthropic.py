"""Anthropic Claude provider implementation"""

import os
import logging
from typing import Dict, Any, List, Optional
from anthropic import AsyncAnthropic
import anthropic

from .base import BaseProvider, ProviderResponse, ProviderError, ProviderType

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider implementation"""
    
    AVAILABLE_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ]
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.provider_type = ProviderType.ANTHROPIC
        
    async def initialize(self) -> None:
        """Initialize Anthropic client"""
        if not self.api_key:
            raise ProviderError("Anthropic API key not provided")
        
        try:
            self._client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Anthropic provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderError(f"Failed to initialize Anthropic: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        **kwargs
    ) -> ProviderResponse:
        """Generate response using Anthropic API"""
        
        if not self._client:
            await self.initialize()
        
        try:
            # Prepare the request
            request_params = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt
            
            # Call Anthropic API
            response = await self._client.messages.create(**request_params)
            
            # Extract content (Claude returns a list of content blocks)
            content = ""
            if response.content:
                content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            # Extract usage info
            usage = {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            return ProviderResponse(
                content=content,
                model_used=response.model,
                usage=usage,
                raw_response=response,
                metadata={'provider': 'anthropic', 'stop_reason': response.stop_reason}
            )
            
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic authentication failed: {e}")
            raise ProviderError(f"Anthropic authentication failed: {str(e)}")
        except anthropic.RateLimitError as e:
            logger.error(f"Anthropic rate limit exceeded: {e}")
            raise ProviderError(f"Anthropic rate limit exceeded: {str(e)}")
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise ProviderError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise ProviderError(f"Anthropic generation failed: {str(e)}")
    
    async def check_availability(self, model: str) -> bool:
        """Check if an Anthropic model is available"""
        
        # Anthropic doesn't have a list models endpoint
        # We check against our known list
        return model in self.AVAILABLE_MODELS
    
    def list_available_models(self) -> List[str]:
        """List available Anthropic models"""
        return self.AVAILABLE_MODELS.copy()
    
    async def validate_api_key(self) -> bool:
        """Validate the Anthropic API key works"""
        
        if not self.api_key:
            return False
        
        try:
            client = AsyncAnthropic(api_key=self.api_key)
            # Try a minimal API call to validate the key
            await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            await client.close()
            return True
        except anthropic.AuthenticationError:
            logger.error("Anthropic API key validation failed: Authentication error")
            return False
        except Exception as e:
            logger.error(f"Anthropic API key validation failed: {e}")
            return False