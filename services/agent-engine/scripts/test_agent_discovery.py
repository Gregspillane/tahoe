#!/usr/bin/env python3
"""
Test script to verify agent discovery for ADK Dev UI.
Simulates what 'adk web' would see when looking for agents.
"""

import sys
from pathlib import Path

def test_agent_discovery():
    """Test which directories would be discovered as agent modules."""
    current_dir = Path.cwd()
    agents_dir = current_dir / "agents"
    
    print("🔍 Agent Discovery Test")
    print("=" * 40)
    print(f"Current directory: {current_dir}")
    print(f"Looking for agents in: {agents_dir}")
    print()
    
    if not agents_dir.exists():
        print("❌ agents/ directory not found")
        return False
    
    potential_agents = []
    
    # Check each subdirectory
    for item in agents_dir.iterdir():
        if item.is_dir():
            init_file = item / "__init__.py"
            agent_file = item / "agent.py"
            
            print(f"📁 {item.name}/")
            print(f"   __init__.py: {'✅' if init_file.exists() else '❌'}")
            print(f"   agent.py: {'✅' if agent_file.exists() else '❌'}")
            
            if init_file.exists() and agent_file.exists():
                # Try to load the agent
                try:
                    sys.path.insert(0, str(agents_dir))
                    module = __import__(item.name)
                    agent_module = getattr(module, 'agent', None)
                    root_agent = getattr(agent_module, 'root_agent', None)
                    
                    if root_agent:
                        print(f"   root_agent: ✅ {root_agent.name} ({root_agent.model})")
                        potential_agents.append({
                            'name': item.name,
                            'agent_name': root_agent.name,
                            'model': root_agent.model
                        })
                    else:
                        print(f"   root_agent: ❌ Not found")
                        
                except Exception as e:
                    print(f"   root_agent: ❌ Error loading: {e}")
                    
                sys.path.pop(0)  # Clean up path
            else:
                print(f"   Status: ❌ Invalid module structure")
            
            print()
    
    print(f"🎯 Discovery Results")
    print("=" * 40)
    print(f"Total directories: {len(list(agents_dir.iterdir()))}")
    print(f"Valid agent modules: {len(potential_agents)}")
    print()
    
    if potential_agents:
        print("✅ ADK would discover these agents:")
        for agent in potential_agents:
            print(f"   • {agent['name']} → {agent['agent_name']} ({agent['model']})")
    else:
        print("❌ No valid agents would be discovered")
    
    return len(potential_agents) > 0

if __name__ == "__main__":
    success = test_agent_discovery()
    print()
    if success:
        print("🎉 Agent discovery test PASSED")
        print("   ADK Dev UI should show agents in dropdown")
    else:
        print("💥 Agent discovery test FAILED")
        print("   ADK Dev UI will not work properly")
    
    sys.exit(0 if success else 1)