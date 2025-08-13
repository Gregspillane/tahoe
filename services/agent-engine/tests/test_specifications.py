"""
Comprehensive tests for the specification system.
Tests parsing, validation, and ADK compliance.
"""

import pytest
import json
import yaml
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.specifications import SpecificationParser, SpecificationValidator
from src.models.specifications import (
    AgentSpecification,
    WorkflowTemplate,
    ToolSpecification,
    ModelConfiguration,
    AgentType
)


class TestSpecificationModels:
    """Test Pydantic specification models."""
    
    def test_agent_specification_valid(self):
        """Test valid agent specification."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "test_agent",  # Using underscore
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {
                        "primary": "gemini-2.0-flash"
                    },
                    "instruction_template": "You are a test agent"
                }
            }
        }
        
        spec = AgentSpecification(**spec_data)
        assert spec.metadata.name == "test_agent"
        assert spec.kind == "AgentSpec"
    
    def test_agent_specification_invalid_name(self):
        """Test agent specification with invalid name (hyphens)."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "test-agent",  # Invalid: using hyphens
                "version": "1.0.0"
            },
            "spec": {}
        }
        
        with pytest.raises(ValueError) as exc_info:
            AgentSpecification(**spec_data)
        assert "must use underscores" in str(exc_info.value)
    
    def test_workflow_template_valid(self):
        """Test valid workflow template."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "WorkflowTemplate",
            "metadata": {
                "name": "test_workflow",
                "version": "1.0.0"
            },
            "spec": {
                "type": "sequential",
                "steps": [
                    {"id": "step1", "agent_spec": "agent1"}
                ]
            }
        }
        
        spec = WorkflowTemplate(**spec_data)
        assert spec.metadata.name == "test_workflow"
        assert spec.spec["type"] == "sequential"
    
    def test_tool_specification_valid(self):
        """Test valid tool specification."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "ToolSpec",
            "metadata": {
                "name": "test_tool",
                "version": "1.0.0"
            },
            "spec": {
                "description": "Test tool",
                "function_definition": "def test(): pass"
            }
        }
        
        spec = ToolSpecification(**spec_data)
        assert spec.metadata.name == "test_tool"
    
    def test_model_configuration_valid(self):
        """Test valid model configuration."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "ModelConfig",
            "metadata": {
                "name": "test_config",
                "version": "1.0.0"
            },
            "spec": {
                "primary": {
                    "provider": "google",
                    "model": "gemini-2.0-flash"
                }
            }
        }
        
        spec = ModelConfiguration(**spec_data)
        assert spec.metadata.name == "test_config"


class TestSpecificationParser:
    """Test specification parser functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = SpecificationParser(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_yaml_specification(self):
        """Test loading YAML specification."""
        # Create test YAML file
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test_agent"},
            "spec": {}
        }
        
        yaml_path = Path(self.temp_dir) / "test.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(spec_data, f)
        
        # Load specification
        loaded = self.parser.load_spec("test.yaml")
        assert loaded["metadata"]["name"] == "test_agent"
    
    def test_load_json_specification(self):
        """Test loading JSON specification."""
        spec_data = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "test_agent"},
            "spec": {}
        }
        
        json_path = Path(self.temp_dir) / "test.json"
        with open(json_path, 'w') as f:
            json.dump(spec_data, f)
        
        loaded = self.parser.load_spec("test.json")
        assert loaded["metadata"]["name"] == "test_agent"
    
    def test_resolve_references(self):
        """Test reference resolution."""
        # Create base specification
        base_spec = {
            "apiVersion": "agent-engine/v1",
            "metadata": {"name": "base"},
            "spec": {"base_field": "base_value"}
        }
        
        base_path = Path(self.temp_dir) / "base.yaml"
        with open(base_path, 'w') as f:
            yaml.dump(base_spec, f)
        
        # Create spec with reference
        ref_spec = {
            "$ref": "base.yaml",
            "spec": {"base_field": "base_value", "additional_field": "additional_value"}
        }
        
        ref_path = Path(self.temp_dir) / "ref.yaml"
        with open(ref_path, 'w') as f:
            yaml.dump(ref_spec, f)
        
        # Load and check resolution
        loaded = self.parser.load_spec("ref.yaml")
        assert loaded["metadata"]["name"] == "base"
        # After merge, spec should have both fields
        assert "base_field" in loaded["spec"] or "additional_field" in loaded["spec"]
    
    def test_list_specifications(self):
        """Test listing specifications."""
        # Create agent specs directory
        agents_dir = Path(self.temp_dir) / "agents"
        agents_dir.mkdir()
        
        # Create some spec files
        for i in range(3):
            spec_path = agents_dir / f"agent_{i}.yaml"
            with open(spec_path, 'w') as f:
                yaml.dump({"name": f"agent_{i}"}, f)
        
        # List specifications
        agents = self.parser.list_specifications("agents")
        assert len(agents) == 3
        assert "agent_0" in agents


class TestSpecificationValidator:
    """Test specification validation."""
    
    def setup_method(self):
        """Set up validator."""
        self.validator = SpecificationValidator()
    
    def test_validate_valid_agent_spec(self):
        """Test validation of valid agent specification."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "valid_agent",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test instruction"
                }
            }
        }
        
        assert self.validator.validate_agent_spec(spec) == True
    
    def test_validate_invalid_agent_name(self):
        """Test validation catches invalid agent names."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "invalid-agent",  # Hyphens not allowed
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.validator.validate_agent_spec(spec)
        assert "must use underscores" in str(exc_info.value)
    
    def test_validate_loop_agent_spec(self):
        """Test validation of loop agent (ADK pattern check)."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "loop_agent",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {"type": "loop"},
                "sub_agents": [  # Correct: list of sub-agents
                    {"spec_ref": "agent1"}
                ]
            }
        }
        
        assert self.validator.validate_agent_spec(spec) == True
    
    def test_validate_workflow_spec(self):
        """Test validation of workflow specification."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "WorkflowTemplate",
            "metadata": {
                "name": "test_workflow",
                "version": "1.0.0"
            },
            "spec": {
                "type": "sequential",
                "steps": [
                    {"id": "step1", "agent_spec": "agent1"},
                    {"id": "step2", "agent_spec": "agent2", "depends_on": ["step1"]}
                ]
            }
        }
        
        assert self.validator.validate_workflow_spec(spec) == True
    
    def test_check_adk_compliance(self):
        """Test ADK compliance checking."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "test-agent"  # Warning: uses hyphens
            },
            "spec": {
                "agent": {
                    "type": "loop",
                    "parameters": {
                        "model": "gemini"  # Warning: model in parameters
                    }
                },
                "sub_agent": {}  # Warning: should be sub_agents
            }
        }
        
        warnings = self.validator.check_adk_compliance(spec)
        assert len(warnings) >= 2
        assert any("hyphens" in w for w in warnings)
        assert any("sub_agents" in w for w in warnings)


class TestADKPatternCompliance:
    """Test ADK pattern compliance specifically."""
    
    def setup_method(self):
        """Set up validator."""
        self.validator = SpecificationValidator()
    
    def test_agent_naming_pattern(self):
        """Test agent naming follows ADK requirements."""
        # Valid names (underscores)
        valid_names = ["my_agent", "content_analyzer", "workflow_1"]
        for name in valid_names:
            spec = self._create_spec(name)
            assert self.validator.validate_agent_spec(spec) == True
        
        # Invalid names (hyphens)
        invalid_names = ["my-agent", "content-analyzer", "workflow-1"]
        for name in invalid_names:
            spec = self._create_spec(name)
            with pytest.raises(ValueError):
                self.validator.validate_agent_spec(spec)
    
    def test_loop_agent_structure(self):
        """Test LoopAgent uses sub_agents as list."""
        # Correct structure
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": "loop_test"},
            "spec": {
                "agent": {"type": "loop"},
                "sub_agents": [{"spec_ref": "agent1"}]  # List
            }
        }
        assert self.validator.validate_agent_spec(spec) == True
        
        # Incorrect structure (not a list)
        spec["spec"]["sub_agents"] = {"spec_ref": "agent1"}  # Not a list
        with pytest.raises(ValueError) as exc_info:
            self.validator.validate_agent_spec(spec)
        assert "must be a list" in str(exc_info.value)
    
    def _create_spec(self, name: str) -> Dict[str, Any]:
        """Helper to create basic agent spec."""
        return {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {"name": name},
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }


def test_integration_parse_validate_compose():
    """Integration test: parse, validate, and prepare for composition."""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create parser and validator
        parser = SpecificationParser(temp_dir)
        validator = SpecificationValidator()
        
        # Create a valid specification
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "integration_test_agent",
                "version": "1.0.0",
                "description": "Agent for integration testing"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {
                        "primary": "gemini-2.0-flash",
                        "fallbacks": ["gemini-2.5-pro"]
                    },
                    "instruction_template": "You are a {role} agent",
                    "parameters": {
                        "temperature": 0.2
                    }
                },
                "tools": [
                    {
                        "name": "test_tool",
                        "source": "inline",
                        "definition": "def test_tool(x): return x * 2"
                    }
                ]
            }
        }
        
        # Save specification
        spec_path = Path(temp_dir) / "agents" / "test.yaml"
        spec_path.parent.mkdir(parents=True)
        with open(spec_path, 'w') as f:
            yaml.dump(spec, f)
        
        # Parse specification
        loaded = parser.load_agent_spec("test")
        assert loaded["metadata"]["name"] == "integration_test_agent"
        
        # Validate specification
        assert validator.validate_agent_spec(loaded) == True
        
        # Check ADK compliance
        warnings = validator.check_adk_compliance(loaded)
        assert len(warnings) == 0  # Should have no warnings
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])