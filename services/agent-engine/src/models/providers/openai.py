"""OpenAI provider implementation"""

import os
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import openai

from .base import BaseProvider, ProviderResponse, ProviderError, ProviderType

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI API provider implementation"""
    
    AVAILABLE_MODELS = [
        "gpt-4-turbo-preview",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-4-32k",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        self.provider_type = ProviderType.OPENAI
        
    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        if not self.api_key:
            raise ProviderError("OpenAI API key not provided")
        
        try:
            self._client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise ProviderError(f"Failed to initialize OpenAI: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        **kwargs
    ) -> ProviderResponse:
        """Generate response using OpenAI API"""
        
        if not self._client:
            await self.initialize()
        
        try:
            # Format messages
            messages = self.format_messages(prompt, system_prompt)
            
            # Call OpenAI API
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs
            )
            
            # Extract content and usage
            content = response.choices[0].message.content
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            return ProviderResponse(
                content=content,
                model_used=response.model,
                usage=usage,
                raw_response=response,
                metadata={'provider': 'openai', 'finish_reason': response.choices[0].finish_reason}
            )
            
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {e}")
            raise ProviderError(f"OpenAI authentication failed: {str(e)}")
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise ProviderError(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise ProviderError(f"OpenAI generation failed: {str(e)}")
    
    async def check_availability(self, model: str) -> bool:
        """Check if an OpenAI model is available"""
        
        if not self._client:
            try:
                await self.initialize()
            except:
                return False
        
        try:
            # Try to retrieve the model
            models = await self._client.models.list()
            model_ids = [m.id for m in models.data]
            return model in model_ids
        except Exception as e:
            logger.error(f"Failed to check OpenAI model availability: {e}")
            return False
    
    def list_available_models(self) -> List[str]:
        """List available OpenAI models"""
        return self.AVAILABLE_MODELS.copy()
    
    async def validate_api_key(self) -> bool:
        """Validate the OpenAI API key works"""
        
        if not self.api_key:
            return False
        
        try:
            client = AsyncOpenAI(api_key=self.api_key)
            # Try to list models as a validation check
            await client.models.list()
            await client.close()
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            return False