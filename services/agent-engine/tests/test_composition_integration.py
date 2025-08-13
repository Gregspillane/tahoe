"""
Integration tests for specification to agent composition.
Tests the full pipeline from specification to ADK agent creation.
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.composition import UniversalAgentFactory, AgentCompositionService
from src.core.specifications import SpecificationParser


class TestUniversalAgentFactory:
    """Test the UniversalAgentFactory."""
    
    def setup_method(self):
        """Set up factory for testing."""
        self.factory = UniversalAgentFactory()
    
    def test_build_llm_agent(self):
        """Test building an LLM agent from specification."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "test_llm_agent",
                "description": "Test LLM agent"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {
                        "primary": "gemini-2.0-flash"
                    },
                    "instruction_template": "You are a helpful assistant"
                }
            }
        }
        
        agent = self.factory.build_agent(spec)
        assert agent is not None
        assert agent.name == "test_llm_agent"
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'instruction')
    
    def test_sanitize_agent_name(self):
        """Test that agent names are sanitized (hyphens to underscores)."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "test-agent-name"  # With hyphens
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }
        
        # Note: The factory should sanitize the name
        agent = self.factory.build_agent(spec)
        assert agent.name == "test_agent_name"  # Sanitized
    
    def test_build_with_context(self):
        """Test building agent with context for template variables."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "context_agent"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "You are a {role} specializing in {domain}"
                }
            }
        }
        
        context = {
            "role": "analyst",
            "domain": "finance"
        }
        
        agent = self.factory.build_agent(spec, context)
        assert "analyst" in agent.instruction
        assert "finance" in agent.instruction
    
    def test_build_with_inline_tools(self):
        """Test building agent with inline tool definitions."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "agent_with_tools"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                },
                "tools": [
                    {
                        "name": "multiply",
                        "source": "inline",
                        "definition": "def multiply(x: int, y: int) -> int:\n    return x * y"
                    }
                ]
            }
        }
        
        agent = self.factory.build_agent(spec)
        assert agent is not None
        assert hasattr(agent, 'tools')
        assert len(agent.tools) == 1
    
    def test_build_sequential_agent(self):
        """Test building a sequential workflow agent."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "sequential_workflow"
            },
            "spec": {
                "agent": {
                    "type": "sequential"
                },
                "sub_agents": []  # Would normally have sub-agent references
            }
        }
        
        agent = self.factory.build_agent(spec)
        assert agent is not None
        assert agent.name == "sequential_workflow"
    
    def test_build_loop_agent(self):
        """Test building a loop agent with correct ADK pattern."""
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "loop_workflow"
            },
            "spec": {
                "agent": {
                    "type": "loop"
                },
                "sub_agents": []  # List as required by ADK
            }
        }
        
        agent = self.factory.build_agent(spec)
        assert agent is not None
        assert agent.name == "loop_workflow"


class TestAgentCompositionService:
    """Test the AgentCompositionService."""
    
    def setup_method(self):
        """Set up service and temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = AgentCompositionService()
        self.service.parser.base_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_build_agent_from_spec_file(self):
        """Test building agent from specification file."""
        # Create agent specification file
        spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "file_based_agent",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "You are a helpful assistant"
                }
            }
        }
        
        # Save to file
        agents_dir = Path(self.temp_dir) / "agents"
        agents_dir.mkdir(parents=True)
        spec_file = agents_dir / "test_agent.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(spec, f)
        
        # Build agent from file
        agent = self.service.build_agent_from_spec("test_agent")
        assert agent is not None
        assert agent.name == "file_based_agent"
    
    def test_build_workflow_from_template(self):
        """Test building workflow from template."""
        # Create workflow template
        template = {
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
        
        # Save to file
        workflows_dir = Path(self.temp_dir) / "workflows"
        workflows_dir.mkdir(parents=True)
        template_file = workflows_dir / "test_workflow.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(template, f)
        
        # Build workflow
        workflow = self.service.build_workflow_from_template("test_workflow")
        assert workflow is not None
    
    def test_list_available_specifications(self):
        """Test listing available specifications."""
        # Create some spec files
        for spec_type in ["agents", "workflows", "tools", "models"]:
            type_dir = Path(self.temp_dir) / spec_type
            type_dir.mkdir(parents=True)
            
            for i in range(2):
                spec_file = type_dir / f"spec_{i}.yaml"
                with open(spec_file, 'w') as f:
                    yaml.dump({"name": f"{spec_type}_{i}"}, f)
        
        # List specifications
        agents = self.service.list_available_agents()
        workflows = self.service.list_available_workflows()
        tools = self.service.list_available_tools()
        models = self.service.list_available_models()
        
        assert len(agents) == 2
        assert len(workflows) == 2
        assert len(tools) == 2
        assert len(models) == 2
    
    def test_validate_specification(self):
        """Test specification validation through service."""
        # Valid specification
        valid_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "valid_agent"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }
        
        result = self.service.validate_specification(valid_spec)
        assert result["valid"] == True
        assert result["kind"] == "AgentSpec"
        
        # Invalid specification
        invalid_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "invalid-agent"  # Hyphens
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "Test"
                }
            }
        }
        
        result = self.service.validate_specification(invalid_spec)
        assert result["valid"] == False
        assert "error" in result


class TestCompositionIntegration:
    """Full integration tests for composition pipeline."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.service = AgentCompositionService()
        self.service.parser.base_path = Path(self.temp_dir)
        self._create_test_specifications()
    
    def teardown_method(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_specifications(self):
        """Create a set of test specifications."""
        # Create analyzer agent
        analyzer_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "analyzer",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "You are an analyzer"
                }
            }
        }
        
        # Create processor agent
        processor_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "processor",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "gemini-2.0-flash"},
                    "instruction_template": "You are a processor"
                }
            }
        }
        
        # Create workflow template
        workflow_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "WorkflowTemplate",
            "metadata": {
                "name": "analysis_workflow",
                "version": "1.0.0"
            },
            "spec": {
                "type": "sequential",
                "steps": [
                    {"id": "analyze", "agent_spec": "analyzer"},
                    {"id": "process", "agent_spec": "processor"}
                ]
            }
        }
        
        # Save specifications
        agents_dir = Path(self.temp_dir) / "agents"
        agents_dir.mkdir(parents=True)
        
        for name, spec in [("analyzer", analyzer_spec), ("processor", processor_spec)]:
            with open(agents_dir / f"{name}.yaml", 'w') as f:
                yaml.dump(spec, f)
        
        workflows_dir = Path(self.temp_dir) / "workflows"
        workflows_dir.mkdir(parents=True)
        
        with open(workflows_dir / "analysis_workflow.yaml", 'w') as f:
            yaml.dump(workflow_spec, f)
    
    def test_complete_composition_pipeline(self):
        """Test complete pipeline from spec to agent."""
        # Load and validate analyzer
        analyzer = self.service.build_agent_from_spec("analyzer")
        assert analyzer is not None
        assert analyzer.name == "analyzer"
        
        # Load and validate processor
        processor = self.service.build_agent_from_spec("processor")
        assert processor is not None
        assert processor.name == "processor"
        
        # Load and build workflow
        workflow = self.service.build_workflow_from_template("analysis_workflow")
        assert workflow is not None
    
    def test_composition_with_context_injection(self):
        """Test composition with context variable injection."""
        # Create agent with template variables
        templated_spec = {
            "apiVersion": "agent-engine/v1",
            "kind": "AgentSpec",
            "metadata": {
                "name": "templated_agent",
                "version": "1.0.0"
            },
            "spec": {
                "agent": {
                    "type": "llm",
                    "model": {"primary": "{model_name}"},
                    "instruction_template": "You are a {role} working on {task}"
                }
            }
        }
        
        agents_dir = Path(self.temp_dir) / "agents"
        with open(agents_dir / "templated_agent.yaml", 'w') as f:
            yaml.dump(templated_spec, f)
        
        # Build with context
        context = {
            "model_name": "gemini-2.0-flash",
            "role": "researcher",
            "task": "data analysis"
        }
        
        agent = self.service.build_agent_from_spec("templated_agent", context)
        assert agent is not None
        assert "researcher" in agent.instruction
        assert "data analysis" in agent.instruction


def test_adk_pattern_compliance_in_composition():
    """Test that ADK patterns are correctly followed in composition."""
    factory = UniversalAgentFactory()
    
    # Test 1: Agent names are sanitized
    spec_with_hyphens = {
        "apiVersion": "agent-engine/v1",
        "kind": "AgentSpec",
        "metadata": {"name": "my-test-agent"},
        "spec": {
            "agent": {
                "type": "llm",
                "model": {"primary": "gemini-2.0-flash"},
                "instruction_template": "Test"
            }
        }
    }
    
    agent = factory.build_agent(spec_with_hyphens)
    assert agent.name == "my_test_agent"  # Hyphens converted to underscores
    
    # Test 2: Loop agent uses list of sub_agents
    loop_spec = {
        "apiVersion": "agent-engine/v1",
        "kind": "AgentSpec",
        "metadata": {"name": "loop_test"},
        "spec": {
            "agent": {"type": "loop"},
            "sub_agents": []  # List as required
        }
    }
    
    loop_agent = factory.build_agent(loop_spec)
    assert loop_agent is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])