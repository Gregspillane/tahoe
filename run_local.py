#!/usr/bin/env python3
"""
Local development runner for Tahoe
"""

import os
import sys
import subprocess
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Set environment variables
os.environ["PYTHONPATH"] = str(project_root) + ":" + os.environ.get("PYTHONPATH", "")
os.environ["TAHOE_SERVICE_TOKEN"] = "development_token_change_in_production"

# Check if ADK docs exist locally
adk_docs_path = project_root / "adk_docs_markdown"
if adk_docs_path.exists():
    print(f"✅ ADK documentation found at: {adk_docs_path}")
else:
    print(f"⚠️  ADK documentation not found at: {adk_docs_path}")

def run_api_server():
    """Run the Tahoe API server"""
    print("🚀 Starting Tahoe API server on port 9000...")
    print("📖 API docs will be available at: http://localhost:9000/docs")
    print("🔑 Service token: development_token_change_in_production")
    print()
    
    try:
        subprocess.run([
            "uvicorn", 
            "src.tahoe.api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "9000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Tahoe API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def run_example():
    """Run the basic usage example"""
    example_path = project_root / "examples" / "basic_usage.py"
    if not example_path.exists():
        print(f"❌ Example not found: {example_path}")
        sys.exit(1)
    
    print("🧪 Running basic usage example...")
    try:
        subprocess.run(["python", str(example_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "example":
            run_example()
        elif command == "server":
            run_api_server()
        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python run_local.py [server|example]")
            sys.exit(1)
    else:
        # Default to running server
        run_api_server()

if __name__ == "__main__":
    main()