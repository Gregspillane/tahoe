"""
ADK Dev UI Integration for Tahoe Agent Engine.
Provides visual agent development, testing, and debugging interface.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml
import json
from dataclasses import dataclass

# Import our composition system
try:
    from .composition import AgentCompositionService
    from .specifications import SpecificationParser
except ImportError:
    # Fallback for direct script execution
    from composition import AgentCompositionService
    from specifications import SpecificationParser

# Import ADK components for agent creation
try:
    from google.adk.agents import Agent as LlmAgent
    import subprocess
    
    # Also check if adk command is available
    result = subprocess.run(["adk", "--help"], capture_output=True, text=True, timeout=5)
    ADK_AVAILABLE = result.returncode == 0
except (ImportError, subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
    ADK_AVAILABLE = False
    # Mock for development
    class LlmAgent:
        def __init__(self, name, model, instruction, description="", tools=None, **kwargs):
            self.name = name
            self.model = model
            self.instruction = instruction
            self.description = description
            self.tools = tools or []


@dataclass
class DevUIConfiguration:
    """Configuration for ADK Dev UI integration."""
    port: int = 8002
    host: str = "localhost"
    auto_reload: bool = True
    agent_specs_path: Optional[Path] = None
    examples_path: Optional[Path] = None
    temp_dir: Optional[Path] = None
    gemini_api_key: Optional[str] = None
    debug: bool = False
    
    def __post_init__(self):
        """Initialize paths relative to agent-engine service directory."""
        if self.agent_specs_path is None:
            # Get agent-engine service directory (assuming we're in src/core/)
            service_dir = Path(__file__).parent.parent.parent
            self.agent_specs_path = service_dir / "specs" / "agents"
        
        if self.examples_path is None:
            service_dir = Path(__file__).parent.parent.parent
            self.examples_path = service_dir / "examples"


class AgentDiscovery:
    """Utility for discovering and loading agents from specifications."""
    
    def __init__(self, specs_path: Path):
        """Initialize agent discovery with specifications path."""
        self.specs_path = Path(specs_path)
        self.parser = SpecificationParser()
        self.composition_service = AgentCompositionService()
    
    def discover_agent_specs(self) -> List[Dict[str, Any]]:
        """Discover all agent specifications from the specs directory."""
        agent_specs = []
        
        # Look for YAML files in the agents directory
        agents_dir = self.specs_path
        if not agents_dir.exists():
            print(f"Warning: Agent specs directory not found: {agents_dir}")
            return agent_specs
        
        # Find all YAML files recursively
        for yaml_file in agents_dir.rglob("*.yaml"):
            try:
                # Get relative path from specs directory to avoid double specs/ prefix
                # Find the service directory to make proper relative path
                service_dir = Path(__file__).parent.parent.parent
                specs_dir = service_dir / "specs"
                relative_path = yaml_file.relative_to(specs_dir)
                spec = self.parser.load_spec(str(relative_path))
                if spec.get("kind") == "AgentSpec":
                    agent_specs.append(spec)
                    print(f"Discovered agent spec: {spec['metadata']['name']}")
            except Exception as e:
                print(f"Warning: Failed to load spec {yaml_file}: {e}")
        
        return agent_specs
    
    def create_dev_ui_agents(self, specs: List[Dict[str, Any]]) -> List[LlmAgent]:
        """Create agent instances suitable for Dev UI from specifications."""
        agents = []
        
        for spec in specs:
            try:
                # Create a simplified context for Dev UI
                context = {
                    "role": "assistant",
                    "domain": "general",
                    "objective": "help users test and understand agent capabilities"
                }
                
                # Build agent using our composition service
                agent = self.composition_service.build_agent_from_spec(
                    spec['metadata']['name'], 
                    context
                )
                
                if agent:
                    agents.append(agent)
                    print(f"Created agent for Dev UI: {agent.name}")
                    
            except Exception as e:
                print(f"Warning: Failed to create agent {spec['metadata']['name']}: {e}")
        
        return agents
    
    def create_example_agents(self) -> List[LlmAgent]:
        """Create simple example agents for Dev UI testing."""
        agents = []
        
        # Create a simple content analyzer agent
        try:
            if ADK_AVAILABLE:
                content_analyzer = LlmAgent(
                    name="content_analyzer",
                    model="gemini-2.0-flash",
                    instruction="You are a helpful content analyzer. Analyze the provided content and provide insights about its structure, sentiment, and key themes.",
                    description="Analyzes content and provides structured insights"
                )
                agents.append(content_analyzer)
            
                # Create a simple chat assistant
                chat_assistant = LlmAgent(
                    name="chat_assistant", 
                    model="gemini-2.0-flash",
                    instruction="You are a friendly and helpful assistant. Provide clear, concise, and useful responses to user questions.",
                    description="General purpose chat assistant"
                )
                agents.append(chat_assistant)
                
                # Create a code helper agent
                code_helper = LlmAgent(
                    name="code_helper",
                    model="gemini-2.0-flash", 
                    instruction="You are a coding assistant. Help users with programming questions, code review, and debugging. Provide clear explanations and examples.",
                    description="Programming and code assistance"
                )
                agents.append(code_helper)
                
                print(f"Created {len(agents)} example agents for Dev UI")
            
        except Exception as e:
            print(f"Warning: Failed to create example agents: {e}")
        
        return agents


class DevUILauncher:
    """Launcher for ADK Dev UI with Tahoe-specific configuration."""
    
    def __init__(self, config: Optional[DevUIConfiguration] = None):
        """Initialize Dev UI launcher with configuration."""
        self.config = config or DevUIConfiguration()
        self.discovery = AgentDiscovery(self.config.agent_specs_path)
        self.temp_dir = None
        self.agents = []
    
    def setup_environment(self) -> None:
        """Set up environment variables for ADK Dev UI."""
        # Set GEMINI_API_KEY if available
        if self.config.gemini_api_key:
            os.environ["GEMINI_API_KEY"] = self.config.gemini_api_key
        elif not os.getenv("GEMINI_API_KEY"):
            print("Warning: GEMINI_API_KEY not set. Dev UI may not work without it.")
        
        # Set debug mode if enabled
        if self.config.debug:
            os.environ["ADK_DEBUG"] = "true"
    
    def discover_agents(self) -> None:
        """Discover and load agents for Dev UI."""
        print("Discovering agents for Dev UI...")
        
        # Try to load agents from specifications
        specs = self.discovery.discover_agent_specs()
        if specs:
            print(f"Found {len(specs)} agent specifications")
            self.agents.extend(self.discovery.create_dev_ui_agents(specs))
        
        # Add example agents if no specs found or as fallback
        if not self.agents:
            print("No agents from specs, creating example agents...")
            self.agents.extend(self.discovery.create_example_agents())
        
        print(f"Total agents available for Dev UI: {len(self.agents)}")
    
    def create_temporary_agents_file(self) -> Path:
        """Create a temporary file with agents for ADK Dev UI."""
        if not self.temp_dir:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="tahoe_dev_ui_"))
        
        agents_file = self.temp_dir / "agents.py"
        
        # Generate Python code for agents
        agent_code = self._generate_agents_code()
        
        with open(agents_file, "w") as f:
            f.write(agent_code)
        
        print(f"Created temporary agents file: {agents_file}")
        return agents_file
    
    def _generate_agents_code(self) -> str:
        """Generate Python code for agents to be used by ADK Dev UI."""
        code_lines = [
            "# Auto-generated agents for Tahoe Dev UI",
            "# This file is temporary and will be cleaned up",
            "",
            "import os",
            "from google.genai.agents import Agent as LlmAgent",
            "",
            "# Set up environment",
            "if not os.getenv('GEMINI_API_KEY'):",
            "    print('Warning: GEMINI_API_KEY not set')",
            "",
            "# Define agents for Dev UI",
        ]
        
        # Add each agent as a variable
        for i, agent in enumerate(self.agents):
            agent_var = f"agent_{i}_{agent.name}"
            code_lines.extend([
                f"",
                f"{agent_var} = LlmAgent(",
                f"    name='{agent.name}',",
                f"    model='{getattr(agent, 'model', 'gemini-2.0-flash')}',",
                f"    instruction='''{getattr(agent, 'instruction', 'You are a helpful assistant.')}''',",
                f"    description='{getattr(agent, 'description', '')}'",
                f")"
            ])
        
        # Add agent list for easy access
        agent_vars = [f"agent_{i}_{agent.name}" for i, agent in enumerate(self.agents)]
        code_lines.extend([
            "",
            "# List of all agents",
            f"agents = [{', '.join(agent_vars)}]",
            "",
            "# Export for ADK Dev UI",
            "if __name__ == '__main__':",
            "    print(f'Loaded {len(agents)} agents for Dev UI')",
            "    for agent in agents:",
            "        print(f'  - {agent.name}: {agent.description}')"
        ])
        
        return "\n".join(code_lines)
    
    def launch(self) -> None:
        """Launch ADK Dev UI with discovered agents."""
        try:
            print("Setting up Tahoe Dev UI...")
            
            # Setup environment
            self.setup_environment()
            
            # Discover agents
            self.discover_agents()
            
            if not self.agents:
                print("Warning: No agents available for Dev UI")
                return
            
            # Create temporary agents file
            agents_file = self.create_temporary_agents_file()
            
            # Change to the directory containing the agents file
            original_cwd = os.getcwd()
            os.chdir(agents_file.parent)
            
            try:
                print(f"Launching ADK Dev UI on http://{self.config.host}:{self.config.port}")
                print(f"Available agents: {[agent.name for agent in self.agents]}")
                print("Press Ctrl+C to stop the Dev UI")
                
                # Launch adk web command
                cmd = ["adk", "web", "--port", str(self.config.port)]
                if self.config.host != "localhost":
                    cmd.extend(["--host", self.config.host])
                
                # Run the command
                subprocess.run(cmd, check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"Failed to launch ADK Dev UI: {e}")
                print("Make sure 'adk' command is available in your PATH")
                print("Install with: pip install google-adk")
            except KeyboardInterrupt:
                print("\nStopping Dev UI...")
            finally:
                # Restore original directory
                os.chdir(original_cwd)
                
        except Exception as e:
            print(f"Error launching Dev UI: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(f"Warning: Failed to clean up {self.temp_dir}: {e}")
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate Dev UI setup and return status."""
        status = {
            "adk_available": ADK_AVAILABLE,
            "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY")),
            "specs_directory_exists": self.config.agent_specs_path.exists(),
            "agents_discovered": 0,
            "issues": []
        }
        
        # Check ADK availability
        if not ADK_AVAILABLE:
            status["issues"].append("Google ADK not available - install with 'pip install google-adk'")
        
        # Check API key
        if not status["gemini_api_key_set"]:
            status["issues"].append("GEMINI_API_KEY environment variable not set")
        
        # Check specs directory
        if not status["specs_directory_exists"]:
            status["issues"].append(f"Agent specs directory not found: {self.config.agent_specs_path}")
        
        # Try to discover agents
        try:
            specs = self.discovery.discover_agent_specs()
            status["agents_discovered"] = len(specs)
            if len(specs) == 0:
                status["issues"].append("No agent specifications found")
        except Exception as e:
            status["issues"].append(f"Failed to discover agents: {e}")
        
        return status


def create_dev_ui_launcher(
    specs_path: Optional[Path] = None,
    port: int = 8002,
    gemini_api_key: Optional[str] = None
) -> DevUILauncher:
    """Create a Dev UI launcher with the specified configuration."""
    
    config = DevUIConfiguration(
        port=port,
        agent_specs_path=specs_path,  # Will auto-resolve in __post_init__ if None
        gemini_api_key=gemini_api_key or os.getenv("GEMINI_API_KEY")
    )
    
    return DevUILauncher(config)


# CLI entry point for direct usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch Tahoe ADK Dev UI")
    parser.add_argument("--port", type=int, default=8000, help="Port for Dev UI (default: 8000)")
    parser.add_argument("--specs-path", type=Path, help="Path to agent specifications")
    parser.add_argument("--validate", action="store_true", help="Validate setup without launching")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create launcher
    launcher = create_dev_ui_launcher(
        specs_path=args.specs_path,
        port=args.port
    )
    
    if args.debug:
        launcher.config.debug = True
    
    if args.validate:
        # Validate setup
        status = launcher.validate_setup()
        print("Dev UI Setup Status:")
        print(f"  ADK Available: {status['adk_available']}")
        print(f"  GEMINI_API_KEY Set: {status['gemini_api_key_set']}")
        print(f"  Specs Directory Exists: {status['specs_directory_exists']}")
        print(f"  Agents Discovered: {status['agents_discovered']}")
        
        if status["issues"]:
            print("\nIssues:")
            for issue in status["issues"]:
                print(f"  - {issue}")
        else:
            print("\nSetup looks good! ✅")
    else:
        # Launch Dev UI
        launcher.launch()