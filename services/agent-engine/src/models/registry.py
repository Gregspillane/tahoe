"""Model provider registry for managing LLM configurations."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model_string: str
    parameters: Dict[str, Any]
    provider: str


class ModelRegistry:
    """Manages multiple model providers and configurations."""
    
    PROVIDERS = {
        "gemini": {
            "models": {
                "gemini-2.0-flash": {
                    "string": "gemini-2.0-flash",
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
                }
            }
        },
        "anthropic": {
            "models": {
                "claude-3-opus": {
                    "string": "claude-3-opus-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_output_tokens": 2000,
                        "top_p": 1.0
                    }
                },
                "claude-3-sonnet": {
                    "string": "claude-3-sonnet-20240229",
                    "default_params": {
                        "temperature": 0.3,
                        "max_output_tokens": 2000,
                        "top_p": 1.0
                    }
                }
            }
        }
    }
    
    def get_config(self, model_name: str, overrides: Dict[str, Any] = None) -> ModelConfig:
        """Get model configuration with optional parameter overrides."""
        
        # Parse provider from model name
        provider = self._get_provider(model_name)
        
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider for model: {model_name}")
        
        if model_name not in self.PROVIDERS[provider]["models"]:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_config = self.PROVIDERS[provider]["models"][model_name]
        
        # Merge with overrides
        params = {**model_config["default_params"]}
        if overrides:
            params.update(overrides)
        
        return ModelConfig(
            model_string=model_config["string"],
            parameters=params,
            provider=provider
        )
    
    def _get_provider(self, model_name: str) -> str:
        """Determine provider from model name."""
        
        if model_name.startswith("gemini"):
            return "gemini"
        elif model_name.startswith("gpt"):
            return "openai"
        elif model_name.startswith("claude"):
            return "anthropic"
        else:
            raise ValueError(f"Cannot determine provider for model: {model_name}")
    
    async def check_model_availability(self, model_name: str) -> bool:
        """Check if a model is currently available."""
        
        # For now, return True for known models
        # This would implement actual availability checking in production
        try:
            self.get_config(model_name)
            return True
        except ValueError:
            return False