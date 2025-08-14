"""
Configuration loader for agent specifications
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and validates agent configurations from YAML/JSON files"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize config loader
        
        Args:
            template_dir: Directory containing agent templates
        """
        self.template_dir = template_dir or Path(__file__).parent.parent / "templates"
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from file or string
        
        Args:
            config_path: Path to config file or inline config string
            
        Returns:
            Parsed configuration dictionary
        """
        # Check if it's inline YAML/JSON
        if config_path.startswith('{') or config_path.startswith('---'):
            return self._parse_inline(config_path)
        
        # Load from file
        path = Path(config_path)
        if not path.exists():
            # Try relative to template directory
            path = self.template_dir / config_path
            if not path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Check cache
        cache_key = str(path.absolute())
        if cache_key in self._cache:
            logger.debug(f"Using cached config: {cache_key}")
            return self._cache[cache_key]
        
        # Load and parse
        with open(path, 'r') as f:
            content = f.read()
        
        if path.suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(content)
        elif path.suffix == '.json':
            config = json.loads(content)
        else:
            # Try to auto-detect
            config = self._parse_inline(content)
        
        # Cache and return
        self._cache[cache_key] = config
        return config
    
    def _parse_inline(self, content: str) -> Dict[str, Any]:
        """Parse inline YAML or JSON string"""
        content = content.strip()
        
        # Try JSON first
        if content.startswith('{'):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        
        # Try YAML
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid configuration format: {e}")
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load a predefined agent template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template configuration
        """
        # Search in template subdirectories
        for subdir in ['agents', 'workflows', 'tools']:
            template_path = self.template_dir / subdir / f"{template_name}.yaml"
            if template_path.exists():
                return self.load_config(str(template_path))
        
        raise ValueError(f"Template not found: {template_name}")
    
    def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configurations, with override taking precedence
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate configuration against schema
        
        Args:
            config: Configuration to validate
            schema: JSON schema (if None, uses default schema)
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If configuration is invalid
        """
        if schema is None:
            schema = self._get_default_schema()
        
        try:
            validate(instance=config, schema=schema)
            return True
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Get default configuration schema"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["llm", "sequential", "parallel", "loop", "custom"]},
                "description": {"type": "string"},
                "config": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string"},
                        "instruction": {"type": "string"},
                        "tools": {"type": "array"},
                        "sub_agents": {"type": "array"},
                        "max_iterations": {"type": "integer"},
                        "output_key": {"type": "string"}
                    }
                }
            },
            "required": ["name", "type"]
        }