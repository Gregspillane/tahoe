#!/usr/bin/env python3
"""
Validate the corrected Docker architecture for Tahoe platform.
Ensures agent-engine runs independently, not nested in tahoe project.
"""

import subprocess
import sys
import yaml
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success/output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def validate_docker_configs():
    """Validate Docker configuration files."""
    print("🧪 Validating Docker Configuration Files...")
    
    # Check root docker-compose.yml (infrastructure only)
    root_compose = Path("docker-compose.yml")
    if not root_compose.exists():
        print("  ✗ Root docker-compose.yml missing")
        return False
    
    try:
        with open(root_compose) as f:
            root_config = yaml.safe_load(f)
        
        services = root_config.get("services", {})
        
        # Should have postgres and redis, but NOT agent-engine
        if "postgres" in services:
            print("  ✓ Infrastructure includes PostgreSQL")
        else:
            print("  ✗ Infrastructure missing PostgreSQL")
            return False
            
        if "redis" in services:
            print("  ✓ Infrastructure includes Redis")
        else:
            print("  ✗ Infrastructure missing Redis")
            return False
            
        if "agent-engine" in services:
            print("  ✗ Root docker-compose should NOT include agent-engine")
            return False
        else:
            print("  ✓ Root docker-compose correctly excludes agent-engine")
            
        # Check network configuration
        networks = root_config.get("networks", {})
        if "tahoe-network" in networks:
            network_config = networks["tahoe-network"]
            if network_config.get("name") == "tahoe-network":
                print("  ✓ Named network 'tahoe-network' configured correctly")
            else:
                print("  ✗ Network not properly named")
                return False
        else:
            print("  ✗ Missing tahoe-network configuration")
            return False
            
    except Exception as e:
        print(f"  ✗ Error parsing root docker-compose.yml: {e}")
        return False
    
    # Check agent-engine docker-compose.yml
    agent_compose = Path("services/agent-engine/docker-compose.yml")
    if not agent_compose.exists():
        print("  ✗ Agent-engine docker-compose.yml missing")
        return False
    
    try:
        with open(agent_compose) as f:
            agent_config = yaml.safe_load(f)
        
        services = agent_config.get("services", {})
        
        if "agent-engine" in services:
            print("  ✓ Agent-engine has its own docker-compose")
            
            agent_service = services["agent-engine"]
            
            # Check container name
            if agent_service.get("container_name") == "tahoe-agent-engine":
                print("  ✓ Agent-engine container properly named")
            else:
                print("  ✗ Agent-engine container name incorrect")
                return False
                
            # Check network configuration
            networks = agent_config.get("networks", {})
            if "tahoe-network" in networks:
                network_config = networks["tahoe-network"]
                if network_config.get("external") is True:
                    print("  ✓ Agent-engine connects to external tahoe-network")
                else:
                    print("  ✗ Agent-engine network not configured as external")
                    return False
            else:
                print("  ✗ Agent-engine missing network configuration")
                return False
                
        else:
            print("  ✗ Agent-engine service not found in its docker-compose")
            return False
            
    except Exception as e:
        print(f"  ✗ Error parsing agent-engine docker-compose.yml: {e}")
        return False
    
    print("  ✅ All Docker configurations valid")
    return True

def validate_docker_compose_syntax():
    """Validate docker-compose syntax using docker-compose config."""
    print("\n🧪 Validating Docker Compose Syntax...")
    
    # Test root docker-compose
    success, stdout, stderr = run_command("docker-compose config", "Root docker-compose syntax")
    if success:
        print("  ✓ Root docker-compose syntax valid")
    else:
        print(f"  ✗ Root docker-compose syntax error: {stderr}")
        return False
    
    # Test agent-engine docker-compose
    success, stdout, stderr = run_command("cd services/agent-engine && docker-compose config", "Agent-engine syntax")
    if success:
        print("  ✓ Agent-engine docker-compose syntax valid")
    else:
        print(f"  ✗ Agent-engine docker-compose syntax error: {stderr}")
        return False
    
    print("  ✅ All Docker Compose syntax valid")
    return True

def validate_service_independence():
    """Validate that services are properly separated."""
    print("\n🧪 Validating Service Independence...")
    
    # Check Makefiles
    root_makefile = Path("Makefile")
    if root_makefile.exists():
        with open(root_makefile) as f:
            makefile_content = f.read()
        
        # Should reference infrastructure, not agent-engine directly
        if "Infrastructure Services" in makefile_content:
            print("  ✓ Root Makefile focuses on infrastructure")
        else:
            print("  ✗ Root Makefile missing infrastructure focus")
            return False
            
        if "cd services/agent-engine" in makefile_content:
            print("  ✓ Root Makefile directs to individual service management")
        else:
            print("  ✗ Root Makefile missing service direction")
            return False
    else:
        print("  ✗ Root Makefile missing")
        return False
    
    # Check agent-engine Makefile
    agent_makefile = Path("services/agent-engine/Makefile")
    if agent_makefile.exists():
        with open(agent_makefile) as f:
            makefile_content = f.read()
        
        if "docker-compose" in makefile_content:
            print("  ✓ Agent-engine Makefile has docker-compose commands")
        else:
            print("  ✗ Agent-engine Makefile missing docker-compose commands")
            return False
    else:
        print("  ✗ Agent-engine Makefile missing")
        return False
    
    print("  ✅ Service independence properly configured")
    return True

def main():
    """Run all Docker architecture validations."""
    print("🚀 Validating Corrected Docker Architecture")
    print("=" * 60)
    print("Checking that agent-engine runs independently, not nested in tahoe")
    print()
    
    tests = [
        validate_docker_configs,
        validate_docker_compose_syntax,
        validate_service_independence
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Docker Architecture Validation: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ DOCKER ARCHITECTURE CORRECTED SUCCESSFULLY!")
        print()
        print("🎯 Key Corrections:")
        print("  • Agent-engine now runs as independent service")
        print("  • Root docker-compose contains only infrastructure")
        print("  • Named network enables service communication")
        print("  • Makefiles support independent service management")
        print()
        print("🚀 Service Startup Sequence:")
        print("  1. make up                              # Start infrastructure")
        print("  2. cd services/agent-engine && make docker-up  # Start agent-engine")
        print()
        print("📊 Expected Docker Container Layout:")
        print("  ├── tahoe-postgres    (infrastructure)")
        print("  ├── tahoe-redis       (infrastructure)")  
        print("  └── tahoe-agent-engine (independent service)")
        return True
    else:
        print("❌ DOCKER ARCHITECTURE VALIDATION FAILED")
        print("🔧 Fix the failed tests before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)