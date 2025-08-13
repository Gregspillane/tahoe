"""Model provider registry for managing LLM configurations with real API integration"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import os
import logging

from .providers import GeminiProvider, OpenAIProvider, AnthropicProvider
from .providers.base import BaseProvider, ProviderError

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    model_string: str
    parameters: Dict[str, Any]
    provider: str
    provider_instance: Optional[BaseProvider] = None


class ModelRegistry:
    """Manages multiple model providers and configurations with real API integration"""
    
    PROVIDERS = {
        "gemini": {
            "models": {
                "gemini-2.0-flash-exp": {
                    "string": "gemini-2.0-flash-exp",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 0.95
                    }
                },
                "gemini-1.5-flash": {
                    "string": "gemini-1.5-flash",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 0.95
                    }
                },
                "gemini-1.5-pro": {
                    "string": "gemini-1.5-pro",
                    "default_params": {
                        "temperature": 0.5,
                        "max_tokens": 4000,
                        "top_p": 0.95
                    }
                }
            }
        },
        "openai": {
            "models": {
                "gpt-4-turbo": {
                    "string": "gpt-4-turbo-preview",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "gpt-4o": {
                    "string": "gpt-4o",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "gpt-3.5-turbo": {
                    "string": "gpt-3.5-turbo",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                }
            }
        },
        "anthropic": {
            "models": {
                "claude-3-opus": {
                    "string": "claude-3-opus-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "claude-3-sonnet": {
                    "string": "claude-3-sonnet-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "claude-3-5-sonnet": {
                    "string": "claude-3-5-sonnet-20241022",
                    "default_params": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "top_p": 1.0
                    }
                }
            }
        }
    }
    
    def __init__(self):
        self._provider_instances = {}
        self._initialized_providers = set()
        
    async def get_provider(self, provider_name: str) -> BaseProvider:
        """Get or create a provider instance"""
        
        if provider_name not in self._provider_instances:
            # Create provider instance based on type
            if provider_name == "gemini":
                provider = GeminiProvider()
            elif provider_name == "openai":
                provider = OpenAIProvider()
            elif provider_name == "anthropic":
                provider = AnthropicProvider()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
            
            # Initialize if not already done
            if provider_name not in self._initialized_providers:
                try:
                    await provider.initialize()
                    self._initialized_providers.add(provider_name)
                except ProviderError as e:
                    logger.warning(f"Failed to initialize {provider_name}: {e}")
                    # Don't add to initialized set, will retry next time
                    
            self._provider_instances[provider_name] = provider
            
        return self._provider_instances[provider_name]
    
    async def get_config(self, model_name: str, overrides: Dict[str, Any] = None) -> ModelConfig:
        """Get model configuration with optional parameter overrides and provider instance"""
        
        # Parse provider from model name
        provider_name = self._get_provider(model_name)
        
        if provider_name not in self.PROVIDERS:
            raise ValueError(f"Unknown provider for model: {model_name}")
        
        # Check if model exists in our configurations
        if model_name not in self.PROVIDERS[provider_name]["models"]:
            # For flexibility, allow any model name and use defaults
            logger.warning(f"Model {model_name} not in predefined configs, using defaults")
            model_config = {
                "string": model_name,
                "default_params": {
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "top_p": 1.0
                }
            }
        else:
            model_config = self.PROVIDERS[provider_name]["models"][model_name]
        
        # Merge with overrides
        params = {**model_config["default_params"]}
        if overrides:
            params.update(overrides)
        
        # Get provider instance
        provider_instance = await self.get_provider(provider_name)
        
        return ModelConfig(
            model_string=model_config["string"],
            parameters=params,
            provider=provider_name,
            provider_instance=provider_instance
        )
    
    def _get_provider(self, model_name: str) -> str:
        """Determine provider from model name"""
        
        if model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        else:
            raise ValueError(f"Cannot determine provider for model: {model_name}")
    
    async def check_model_availability(self, model_name: str) -> bool:
        """Check if a model is currently available using real API"""
        
        try:
            provider_name = self._get_provider(model_name)
            provider = await self.get_provider(provider_name)
            
            # Use the provider's real availability check
            return await provider.check_availability(model_name)
            
        except Exception as e:
            logger.error(f"Failed to check availability for {model_name}: {e}")
            return False
    
    async def validate_providers(self) -> Dict[str, bool]:
        """Validate all configured providers have working API keys"""
        
        results = {}
        
        for provider_name in ["gemini", "openai", "anthropic"]:
            try:
                provider = await self.get_provider(provider_name)
                results[provider_name] = await provider.validate_api_key()
            except Exception as e:
                logger.error(f"Failed to validate {provider_name}: {e}")
                results[provider_name] = False
                
        return results
    
    async def generate_with_model(
        self,
        model_name: str,
        prompt: str,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Generate a response using a specific model"""
        
        try:
            # Get model configuration and provider
            config = await self.get_config(model_name, kwargs)
            
            if not config.provider_instance:
                raise ProviderError(f"Provider not initialized for {model_name}")
            
            # Generate response using the provider
            response = await config.provider_instance.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model=config.model_string,
                **config.parameters
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Failed to generate with {model_name}: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup all provider connections"""
        for provider in self._provider_instances.values():
            await provider.close()
        self._provider_instances.clear()
        self._initialized_providers.clear()