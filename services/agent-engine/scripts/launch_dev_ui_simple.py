#!/usr/bin/env python3
"""
Simple ADK Dev UI launcher for Tahoe.
Follows standard ADK patterns for agent discovery.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

def setup_environment():
    """Set up environment variables for ADK."""
    # Load .env from project root
    script_dir = Path(__file__).parent
    agent_engine_dir = script_dir.parent  
    services_dir = agent_engine_dir.parent
    project_root = services_dir.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
    
    # Check GEMINI_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not found in environment")
        print("   Set it with: export GEMINI_API_KEY=your_key_here")
        print("   Or add it to your .env file")
        return False
    else:
        print("✅ GEMINI_API_KEY found in environment")
        return True

def check_adk_available():
    """Check if ADK command is available."""
    try:
        result = subprocess.run(["adk", "--help"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print("✅ ADK command available")
            return True
        else:
            print("❌ ADK command failed")
            return False
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ ADK command not found - install with 'pip install google-adk'")
        return False

def check_agents_directory():
    """Check if agents directory exists with proper structure."""
    agents_dir = Path("agents")
    
    if not agents_dir.exists():
        print("❌ agents/ directory not found")
        print("   Run: python scripts/generate_adk_agents.py")
        return False
    
    # Check for at least one agent module
    agent_dirs = [d for d in agents_dir.iterdir() if d.is_dir()]
    if not agent_dirs:
        print("❌ No agent modules found in agents/ directory")
        print("   Run: python scripts/generate_adk_agents.py")
        return False
    
    # Check if first agent has proper structure
    first_agent = agent_dirs[0]
    if not (first_agent / "__init__.py").exists() or not (first_agent / "agent.py").exists():
        print(f"❌ Agent module {first_agent.name} missing required files")
        print("   Run: python scripts/generate_adk_agents.py")
        return False
    
    print(f"✅ Found {len(agent_dirs)} agent modules")
    return True

def regenerate_agents():
    """Regenerate agent modules from specifications."""
    print("🔧 Regenerating agent modules...")
    try:
        result = subprocess.run([
            sys.executable, "scripts/generate_adk_agents.py"
        ], check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to regenerate agents: {e}")
        print(e.stderr)
        return False

def launch_adk_web(port=8002, host="localhost"):
    """Launch ADK web interface."""
    print(f"🚀 Launching ADK Dev UI on http://{host}:{port}")
    print("   Select an agent from the dropdown to start chatting")
    print("   Use the Events tab for debugging")
    print("   Press Ctrl+C to stop\n")
    
    try:
        # Run adk web command
        cmd = ["adk", "web", "--port", str(port)]
        if host != "localhost":
            cmd.extend(["--host", host])
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch ADK Dev UI: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Dev UI stopped by user")
        return True
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Launch Tahoe ADK Dev UI (simplified)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/launch_dev_ui_simple.py                    # Launch on port 8002
  python scripts/launch_dev_ui_simple.py --port 8003        # Launch on custom port
  python scripts/launch_dev_ui_simple.py --regenerate       # Regenerate agents first
  python scripts/launch_dev_ui_simple.py --validate         # Validate setup only
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8002, 
        help="Port for Dev UI (default: 8002)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for Dev UI (default: localhost)"
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate agent modules before launching"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate setup without launching"
    )
    
    args = parser.parse_args()
    
    print("🚀 Tahoe ADK Dev UI Launcher (Simple)")
    print("=" * 50)
    
    # Check prerequisites
    print("🔍 Validating setup...")
    
    # Check if we're in the right directory
    if not (Path.cwd() / "specs" / "agents").exists():
        print("❌ Error: Please run from the agent-engine service directory")
        print("   Expected to find: specs/agents directory")
        return 1
    
    # Check environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return 1
    
    # Check ADK
    if not check_adk_available():
        return 1
    
    # Regenerate agents if requested
    if args.regenerate:
        if not regenerate_agents():
            return 1
    
    # Check agents directory
    if not check_agents_directory():
        print("\n💡 Tip: Run with --regenerate to generate agent modules")
        return 1
    
    if args.validate:
        print("\n🎉 Setup validation successful!")
        print(f"\nTo launch Dev UI:")
        print(f"   python scripts/launch_dev_ui_simple.py --port {args.port}")
        return 0
    
    # Launch Dev UI
    if launch_adk_web(args.port, args.host):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())