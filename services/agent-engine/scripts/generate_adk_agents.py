#!/usr/bin/env python3
"""
Generate ADK agent modules from Tahoe YAML specifications.
Converts YAML specs into proper ADK directory structure for Dev UI.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to Python path so we can import our modules
script_dir = Path(__file__).parent
agent_engine_dir = script_dir.parent
sys.path.insert(0, str(agent_engine_dir))

try:
    from src.core.specifications import SpecificationParser
except ImportError as e:
    print(f"Failed to import Tahoe modules: {e}")
    print("Make sure you're running from the agent-engine directory")
    sys.exit(1)


class ADKAgentGenerator:
    """Generates ADK agent modules from YAML specifications."""
    
    def __init__(self, specs_path: Path, output_path: Path):
        """Initialize generator with paths."""
        self.specs_path = Path(specs_path)
        self.output_path = Path(output_path)
        self.parser = SpecificationParser()
        
    def discover_agent_specs(self) -> List[Dict[str, Any]]:
        """Discover all agent specifications."""
        agent_specs = []
        agents_dir = self.specs_path / "agents"
        
        if not agents_dir.exists():
            print(f"Warning: Agent specs directory not found: {agents_dir}")
            return agent_specs
            
        for yaml_file in agents_dir.rglob("*.yaml"):
            try:
                relative_path = yaml_file.relative_to(agents_dir)
                spec_path = str(relative_path).replace(".yaml", "").replace(".yml", "")
                
                spec = self.parser.load_agent_spec(spec_path)
                if spec.get("kind") == "AgentSpec":
                    spec["_spec_path"] = spec_path
                    spec["_yaml_file"] = yaml_file
                    agent_specs.append(spec)
                    
            except Exception as e:
                print(f"Warning: Failed to load spec {yaml_file}: {e}")
                
        return agent_specs
    
    def generate_agent_module(self, spec: Dict[str, Any]) -> bool:
        """Generate ADK agent module from specification."""
        try:
            metadata = spec["metadata"]
            original_name = metadata["name"]
            
            # Convert hyphens to underscores for valid Python identifiers
            agent_name = original_name.replace("-", "_")
            
            # Create agent directory
            agent_dir = self.output_path / agent_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate __init__.py
            init_content = "from . import agent\n"
            with open(agent_dir / "__init__.py", "w") as f:
                f.write(init_content)
                
            # Generate agent.py
            agent_content = self._generate_agent_code(spec)
            with open(agent_dir / "agent.py", "w") as f:
                f.write(agent_content)
                
            print(f"✅ Generated ADK module: {agent_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate module for {spec.get('metadata', {}).get('name', 'unknown')}: {e}")
            return False
    
    def _generate_agent_code(self, spec: Dict[str, Any]) -> str:
        """Generate agent.py code from specification."""
        metadata = spec["metadata"]
        agent_spec = spec.get("spec", {}).get("agent", {})
        
        # Extract basic info - convert hyphens to underscores for valid Python identifiers
        original_name = metadata["name"]
        agent_name = original_name.replace("-", "_")
        description = metadata.get("description", "A helpful AI assistant")
        
        # Extract model configuration
        model_config = agent_spec.get("model", "gemini-2.5-flash-lite")
        if isinstance(model_config, dict):
            model = model_config.get("primary", "gemini-2.5-flash-lite")
        else:
            model = model_config
            
        # Extract instruction
        instruction_template = agent_spec.get("instruction_template", "You are a helpful AI assistant.")
        
        # Simple variable substitution for common patterns
        instruction = instruction_template
        instruction = instruction.replace("{role}", "assistant")
        instruction = instruction.replace("{domain}", "general")
        instruction = instruction.replace("{task}", "help users")
        instruction = instruction.replace("{objective}", "assist users")
        instruction = instruction.replace("{context_vars}", "")
        
        # Clean up any remaining template variables
        import re
        instruction = re.sub(r'\{[^}]+\}', '', instruction)
        instruction = instruction.strip()
        
        # Generate tools if any
        tools_code = ""
        tools_import = ""
        tools_list = ""
        
        spec_tools = spec.get("spec", {}).get("tools", [])
        if spec_tools:
            tools_code = self._generate_tools_code(spec_tools)
            if tools_code:
                tools_import = "\n# Tool definitions\n" + tools_code
                tools_list = ",\n    tools=[" + ", ".join([f"tool_{i}" for i in range(len(spec_tools))]) + "]"
        
        # Generate the agent code
        code_lines = [
            f"# Generated ADK agent module for {original_name}",
            f"# Source: {spec.get('_spec_path', 'unknown')}",
            "",
            "from google.adk.agents import Agent",
            tools_import,
            "",
            f"# Agent: {agent_name}",
            f"# Description: {description}",
            "root_agent = Agent(",
            f"    model='{model}',",
            f"    name='{agent_name}',",
            f"    description='''{description}''',",
            f"    instruction='''{instruction}'''{tools_list}",
            ")",
            ""
        ]
        
        return "\n".join(code_lines)
    
    def _generate_tools_code(self, tools: List[Dict[str, Any]]) -> str:
        """Generate tool definitions from specification."""
        tool_lines = []
        
        for i, tool in enumerate(tools):
            tool_name = tool.get("name", f"tool_{i}")
            source = tool.get("source", "registry")
            
            if source == "inline" and "definition" in tool:
                # For inline tools, include the definition
                definition = tool["definition"]
                tool_lines.append(f"# Tool: {tool_name}")
                tool_lines.append(definition)
                tool_lines.append(f"tool_{i} = {tool_name}")
                tool_lines.append("")
            elif source == "builtin":
                # For built-in tools, import from ADK
                if tool_name == "google_search":
                    tool_lines.append("from google.adk.tools import google_search")
                    tool_lines.append(f"tool_{i} = google_search")
                    tool_lines.append("")
            else:
                # For other tools, create a placeholder
                tool_lines.append(f"def {tool_name}(*args, **kwargs):")
                tool_lines.append(f'    """Tool: {tool_name} (placeholder)"""')
                tool_lines.append(f'    return f"Tool {tool_name} called with args={{args}}, kwargs={{kwargs}}"')
                tool_lines.append(f"tool_{i} = {tool_name}")
                tool_lines.append("")
        
        return "\n".join(tool_lines)
    
    def generate_all(self) -> int:
        """Generate all agent modules from specifications."""
        print("🔧 Generating ADK agent modules from YAML specifications...")
        
        # Discover specifications
        specs = self.discover_agent_specs()
        if not specs:
            print("❌ No agent specifications found")
            return 1
            
        print(f"📋 Found {len(specs)} agent specifications")
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate modules
        success_count = 0
        for spec in specs:
            if self.generate_agent_module(spec):
                success_count += 1
                
        print(f"\n✅ Successfully generated {success_count}/{len(specs)} ADK agent modules")
        print(f"📁 Output directory: {self.output_path.absolute()}")
        
        if success_count > 0:
            print(f"\n🚀 To launch Dev UI:")
            print(f"   cd {self.output_path.parent}")
            print(f"   adk web --port 8002")
            
        return 0 if success_count > 0 else 1
    
    def clean_output(self) -> None:
        """Clean up generated agent modules."""
        if self.output_path.exists():
            import shutil
            shutil.rmtree(self.output_path)
            print(f"🧹 Cleaned up generated modules: {self.output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate ADK agent modules from Tahoe YAML specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_adk_agents.py                   # Generate all agents
  python scripts/generate_adk_agents.py --clean           # Clean up generated modules
  python scripts/generate_adk_agents.py --output ./my_agents  # Custom output directory
        """
    )
    
    parser.add_argument(
        "--specs-path",
        type=Path,
        default="specs",
        help="Path to specifications directory (default: specs)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default="agents",
        help="Output directory for generated agent modules (default: agents)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean up generated agent modules"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the agent-engine directory
    if not (Path.cwd() / "specs" / "agents").exists():
        print("❌ Error: Please run from the agent-engine service directory")
        print("   Expected to find: specs/agents directory")
        return 1
    
    generator = ADKAgentGenerator(args.specs_path, args.output)
    
    if args.clean:
        generator.clean_output()
        return 0
    else:
        return generator.generate_all()


if __name__ == "__main__":
    sys.exit(main())