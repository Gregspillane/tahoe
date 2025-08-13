#!/usr/bin/env python3
"""
Launch script for Tahoe ADK Dev UI.
Sets up environment and launches the development interface.
"""

import os
import sys
import argparse
from pathlib import Path

# Add src to Python path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.dev_ui import create_dev_ui_launcher, DevUIConfiguration
    from config.settings import TahoeConfig
except ImportError as e:
    print(f"Failed to import Tahoe modules: {e}")
    print("Make sure you're running from the agent-engine directory")
    sys.exit(1)


def setup_environment():
    """Set up environment for Dev UI launch."""
    print("Setting up environment for Tahoe Dev UI...")
    
    # Load configuration from our settings
    try:
        settings = TahoeConfig()
        
        # Set GEMINI_API_KEY if available from settings
        if hasattr(settings, 'adk') and hasattr(settings.adk, 'api_key'):
            if settings.adk.api_key and settings.adk.api_key != "CHANGE_THIS_your_gemini_api_key":
                os.environ["GEMINI_API_KEY"] = settings.adk.api_key
                print("✅ GEMINI_API_KEY loaded from configuration")
            else:
                print("⚠️  GEMINI_API_KEY not configured in settings")
        
        # Check if key is set in environment
        if not os.getenv("GEMINI_API_KEY"):
            print("⚠️  GEMINI_API_KEY not found in environment")
            print("   Set it with: export GEMINI_API_KEY=your_key_here")
            print("   Or add it to your .env file")
        else:
            print("✅ GEMINI_API_KEY found in environment")
            
    except Exception as e:
        print(f"Warning: Could not load settings: {e}")
        print("Continuing with environment variables only...")


def validate_prerequisites():
    """Validate that prerequisites are met."""
    print("Validating prerequisites...")
    
    issues = []
    
    # Check if adk command is available
    import subprocess
    try:
        result = subprocess.run(["adk", "--help"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print("✅ ADK command available")
        else:
            issues.append("ADK command failed")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        issues.append("ADK command not found - install with 'pip install google-adk'")
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append(f"Python 3.9+ required (current: {sys.version})")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check if we're in the agent-engine service directory
    current_dir = Path.cwd()
    specs_agents_dir = current_dir / "specs" / "agents"
    
    if specs_agents_dir.exists():
        print("✅ Agent specifications directory found")
    else:
        # Check if we might be in the project root
        service_specs_dir = current_dir / "services" / "agent-engine" / "specs" / "agents"
        if service_specs_dir.exists():
            issues.append("Please run from the agent-engine service directory: cd services/agent-engine")
        else:
            issues.append("Agent specifications directory not found - ensure you're in the agent-engine service directory")
    
    return issues


def main():
    """Main entry point for Dev UI launcher."""
    parser = argparse.ArgumentParser(
        description="Launch Tahoe ADK Dev UI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/launch_dev_ui.py                    # Launch on default port 8002
  python scripts/launch_dev_ui.py --port 8002        # Launch on port 8002
  python scripts/launch_dev_ui.py --validate         # Validate setup only
  python scripts/launch_dev_ui.py --debug            # Enable debug mode
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
        "--specs-path", 
        type=Path, 
        help="Path to agent specifications (default: auto-detect from service directory)"
    )
    parser.add_argument(
        "--validate", 
        action="store_true", 
        help="Validate setup without launching"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip prerequisite validation"
    )
    
    args = parser.parse_args()
    
    print("🚀 Tahoe ADK Dev UI Launcher")
    print("=" * 40)
    
    # Setup environment
    setup_environment()
    
    # Validate prerequisites unless skipped
    if not args.skip_validation:
        issues = validate_prerequisites()
        if issues:
            print("\n❌ Prerequisites not met:")
            for issue in issues:
                print(f"   - {issue}")
            print("\nFix these issues and try again, or use --skip-validation to continue anyway.")
            return 1
    
    # Create launcher with configuration
    try:
        config = DevUIConfiguration(
            port=args.port,
            host=args.host,
            agent_specs_path=args.specs_path,
            debug=args.debug
        )
        
        launcher = create_dev_ui_launcher(
            specs_path=args.specs_path,
            port=args.port
        )
        launcher.config = config
        
        if args.validate:
            # Validate setup
            print("\n🔍 Validating Dev UI setup...")
            status = launcher.validate_setup()
            
            print("\nDev UI Setup Status:")
            print(f"  ✅ ADK Available: {status['adk_available']}")
            print(f"  ✅ GEMINI_API_KEY Set: {status['gemini_api_key_set']}")
            print(f"  ✅ Specs Directory Exists: {status['specs_directory_exists']}")
            print(f"  ✅ Agents Discovered: {status['agents_discovered']}")
            
            if status["issues"]:
                print("\n⚠️  Issues found:")
                for issue in status["issues"]:
                    print(f"     - {issue}")
                return 1
            else:
                print("\n🎉 Setup validation successful!")
                print(f"\nTo launch Dev UI, run:")
                print(f"   python scripts/launch_dev_ui.py --port {args.port}")
                return 0
        else:
            # Launch Dev UI
            print(f"\n🌐 Launching Dev UI on http://{args.host}:{args.port}")
            print("   Use the browser interface to interact with agents")
            print("   Check the Events tab for debugging information")
            print("   Press Ctrl+C to stop\n")
            
            launcher.launch()
            return 0
            
    except KeyboardInterrupt:
        print("\n\n👋 Dev UI stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())