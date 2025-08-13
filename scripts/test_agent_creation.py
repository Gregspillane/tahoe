#!/usr/bin/env python3
"""Test script for agent creation functionality."""

import asyncio
import sys
import os
import logging

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'agent-engine'))

from src.agents.factory import AgentFactory, TemplateNotFoundError
from src.models.registry import ModelRegistry
from src.tools.registry import ToolRegistry
from prisma import Prisma
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_model_registry():
    """Test ModelRegistry functionality"""
    print("\n=== Testing ModelRegistry ===")
    
    registry = ModelRegistry()
    
    # Test Gemini model
    try:
        config = registry.get_config("gemini-2.0-flash")
        print(f"✅ Gemini config: {config.model_string}, provider: {config.provider}")
        print(f"   Parameters: {config.parameters}")
    except Exception as e:
        print(f"❌ Gemini config failed: {e}")
    
    # Test with overrides
    try:
        config = registry.get_config("gemini-2.0-flash", {"temperature": 0.7})
        print(f"✅ Gemini with overrides: temperature = {config.parameters['temperature']}")
    except Exception as e:
        print(f"❌ Gemini overrides failed: {e}")
    
    # Test unknown model
    try:
        config = registry.get_config("unknown-model")
        print(f"❌ Should have failed for unknown model")
    except ValueError as e:
        print(f"✅ Correctly rejected unknown model: {e}")


async def test_tool_registry():
    """Test ToolRegistry functionality"""
    print("\n=== Testing ToolRegistry ===")
    
    registry = ToolRegistry()
    
    # Test loading tools
    try:
        tools = await registry.load_tools(["regulatory_lookup", "compliance_check"])
        print(f"✅ Loaded {len(tools)} tools")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"❌ Tool loading failed: {e}")
    
    # Test single tool
    try:
        tool = await registry.get_tool("sentiment_analysis")
        if tool:
            print(f"✅ Single tool: {tool['name']}")
        else:
            print(f"❌ Tool not found")
    except Exception as e:
        print(f"❌ Single tool retrieval failed: {e}")


async def test_agent_factory_basic():
    """Test AgentFactory basic functionality without database"""
    print("\n=== Testing AgentFactory (Basic) ===")
    
    # Create factory without database
    factory = AgentFactory()
    
    # Test model registry integration
    try:
        config = factory.model_registry.get_config("gemini-2.0-flash")
        print(f"✅ Factory has working model registry")
    except Exception as e:
        print(f"❌ Factory model registry failed: {e}")
    
    # Test tool registry integration
    try:
        tools = await factory.tool_registry.load_tools(["regulatory_lookup"])
        print(f"✅ Factory has working tool registry")
    except Exception as e:
        print(f"❌ Factory tool registry failed: {e}")


async def test_agent_creation():
    """Test creating an agent from a sample template"""
    print("\n=== Testing Agent Creation ===")
    
    # Sample template
    sample_template = {
        "id": "test-compliance-agent",
        "name": "compliance-analyst",
        "description": "Compliance analysis specialist",
        "type": "specialist",
        "model": "gemini-2.0-flash",
        "modelConfig": {"temperature": 0.3},
        "capabilities": ["compliance-analysis", "violation-detection"],
        "tools": ["regulatory_lookup", "compliance_check"],
        "triggerRules": {},
        "systemPrompt": "You are a compliance analyst specializing in financial regulations.",
        "userPrompt": "Analyze this interaction for compliance: {interaction}",
        "version": 1,
        "isActive": True
    }
    
    factory = AgentFactory()
    
    try:
        agent = await factory.create_agent(sample_template)
        print(f"✅ Created agent: {agent.template['name']}")
        
        # Test analysis
        test_input = {
            "interaction": {
                "content": "Hello, this is a test call transcript for compliance analysis.",
                "type": "call"
            },
            "trace_id": "test-123"
        }
        
        result = await agent.analyze(test_input)
        print(f"✅ Analysis completed:")
        print(f"   Agent: {result.agent_name}")
        print(f"   Score: {result.score}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Execution time: {result.execution_time:.3f}s")
        print(f"   Findings: {len(result.findings)}")
        print(f"   Violations: {len(result.violations)}")
        print(f"   Recommendations: {len(result.recommendations)}")
        
    except Exception as e:
        print(f"❌ Agent creation/analysis failed: {e}")
        import traceback
        traceback.print_exc()


async def test_with_database():
    """Test with actual database connection (if available)"""
    print("\n=== Testing with Database (if available) ===")
    
    try:
        # Try to connect to database
        db = Prisma()
        await db.connect()
        
        # Try to connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6382")
        cache = redis.from_url(redis_url, decode_responses=True)
        await cache.ping()
        
        print("✅ Database and Redis connections successful")
        
        # Create factory with real connections
        factory = AgentFactory(db=db, cache=cache)
        await factory.initialize()
        
        # Try to find existing templates
        try:
            templates = await db.agenttemplate.find_many({
                "where": {"isActive": True},
                "take": 3
            })
            print(f"✅ Found {len(templates)} active templates in database")
            
            for template in templates:
                try:
                    template_dict = await factory.load_template(template.id)
                    print(f"   - {template.name} (cached: {template_dict is not None})")
                except Exception as e:
                    print(f"   - {template.name} (load failed: {e})")
                    
        except Exception as e:
            print(f"⚠️ Could not query templates: {e}")
        
        # Cleanup
        await db.disconnect()
        await cache.close()
        
    except Exception as e:
        print(f"⚠️ Database/Redis not available: {e}")
        print("   This is normal if services are not running")


async def main():
    """Run all tests"""
    print("🧪 Agent Factory Test Suite")
    print("=" * 50)
    
    await test_model_registry()
    await test_tool_registry()
    await test_agent_factory_basic()
    await test_agent_creation()
    await test_with_database()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())