"""Google Gemini provider implementation"""

import os
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.api_core import exceptions as google_exceptions

from .base import BaseProvider, ProviderResponse, ProviderError, ProviderType

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    """Google Gemini API provider implementation"""
    
    AVAILABLE_MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash", 
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key or os.getenv("GOOGLE_API_KEY"))
        self.provider_type = ProviderType.GEMINI
        self._models_cache = {}
        
    async def initialize(self) -> None:
        """Initialize Gemini client with API key"""
        if not self.api_key:
            raise ProviderError("Google API key not provided")
        
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Gemini provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            raise ProviderError(f"Failed to initialize Gemini: {str(e)}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 0.95,
        **kwargs
    ) -> ProviderResponse:
        """Generate response using Gemini API"""
        
        if not self.api_key:
            await self.initialize()
        
        try:
            # Get or create model instance
            if model not in self._models_cache:
                self._models_cache[model] = GenerativeModel(model)
            
            model_instance = self._models_cache[model]
            
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Configure generation settings
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p
            )
            
            # Generate response
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract usage info if available
            usage = {}
            if hasattr(response, 'usage_metadata'):
                usage = {
                    'prompt_tokens': getattr(response.usage_metadata, 'prompt_token_count', 0),
                    'completion_tokens': getattr(response.usage_metadata, 'candidates_token_count', 0),
                    'total_tokens': getattr(response.usage_metadata, 'total_token_count', 0)
                }
            
            return ProviderResponse(
                content=response.text,
                model_used=model,
                usage=usage,
                raw_response=response,
                metadata={'provider': 'gemini'}
            )
            
        except google_exceptions.InvalidArgument as e:
            logger.error(f"Invalid argument for Gemini: {e}")
            raise ProviderError(f"Invalid Gemini request: {str(e)}")
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini quota exceeded: {e}")
            raise ProviderError(f"Gemini quota exceeded: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise ProviderError(f"Gemini generation failed: {str(e)}")
    
    async def check_availability(self, model: str) -> bool:
        """Check if a Gemini model is available"""
        
        if not self.api_key:
            return False
        
        try:
            # Configure API if not already done
            genai.configure(api_key=self.api_key)
            
            # List available models
            available_models = genai.list_models()
            model_names = [m.name for m in available_models]
            
            # Check if requested model is in the list
            # Models are returned as 'models/gemini-1.5-flash' format
            model_id = f"models/{model}" if not model.startswith("models/") else model
            return model_id in model_names
            
        except Exception as e:
            logger.error(f"Failed to check Gemini model availability: {e}")
            return False
    
    def list_available_models(self) -> List[str]:
        """List available Gemini models"""
        return self.AVAILABLE_MODELS.copy()
    
    async def validate_api_key(self) -> bool:
        """Validate the Gemini API key works"""
        
        if not self.api_key:
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            # Try to list models as a validation check
            list(genai.list_models())
            return True
        except Exception as e:
            logger.error(f"Gemini API key validation failed: {e}")
            return False