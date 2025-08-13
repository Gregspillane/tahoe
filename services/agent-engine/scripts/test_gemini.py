#!/usr/bin/env python3
"""Test Google Gemini API configuration"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.models.providers.gemini import GeminiProvider


async def test_gemini_configuration():
    """Test that Gemini API is properly configured"""
    
    print("=" * 60)
    print("Testing Google Gemini Configuration")
    print("=" * 60)
    
    # Check environment configuration
    print("\n1. Environment Configuration:")
    print(f"   - Environment: {settings.ENVIRONMENT}")
    print(f"   - Service URL: {settings.SERVICE_URL}")
    print(f"   - Database URL: {'Configured' if settings.DATABASE_URL else 'Not configured'}")
    print(f"   - Redis URL: {'Configured' if settings.REDIS_URL else 'Not configured'}")
    
    # Check API key configuration
    print("\n2. API Key Configuration:")
    api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("   ❌ GOOGLE_API_KEY not found in environment")
        print("\n   To configure:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google API key: GOOGLE_API_KEY=your_key_here")
        print("   3. Get a key from: https://makersuite.google.com/app/apikey")
        return False
    
    # Mask the API key for display
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    print(f"   ✓ GOOGLE_API_KEY found: {masked_key}")
    
    # Test Gemini provider
    print("\n3. Testing Gemini Provider:")
    
    try:
        provider = GeminiProvider(api_key)
        
        # Initialize provider
        await provider.initialize()
        print("   ✓ Provider initialized successfully")
        
        # Validate API key
        is_valid = await provider.validate_api_key()
        if is_valid:
            print("   ✓ API key validated successfully")
        else:
            print("   ❌ API key validation failed")
            return False
        
        # List available models
        models = provider.list_available_models()
        print(f"   ✓ Available models: {', '.join(models)}")
        
        # Test a simple generation
        print("\n4. Testing Generation:")
        response = await provider.generate(
            prompt="Say 'Hello from Gemini!' in exactly 5 words.",
            model="gemini-1.5-flash",
            temperature=0.1,
            max_tokens=50
        )
        
        print(f"   Response: {response.content}")
        print(f"   Model: {response.model_used}")
        if response.usage:
            print(f"   Tokens: {response.usage.get('total_tokens', 'N/A')} total")
        
        print("\n" + "=" * 60)
        print("✅ Gemini configuration test PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ Gemini configuration test FAILED")
        print("=" * 60)
        return False


async def test_agent_factory_integration():
    """Test that Agent Factory can create agents with Gemini"""
    
    print("\n" + "=" * 60)
    print("Testing Agent Factory with Gemini")
    print("=" * 60)
    
    api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("   ❌ Skipping - no API key configured")
        return
    
    try:
        # Import agent factory
        from src.agents.factory import AgentFactory
        from src.models.database import database_manager
        import redis.asyncio as redis
        
        print("\n1. Initializing Agent Factory:")
        
        # Initialize database connection (mock)
        await database_manager.connect()
        cache = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Create factory
        factory = AgentFactory(db=database_manager.db, cache=cache)
        await factory.initialize()
        print("   ✓ Agent Factory initialized")
        
        # Create a test agent template
        template = {
            "id": "test-gemini-agent",
            "name": "test_gemini_agent",
            "description": "Test agent using Gemini",
            "type": "specialist",
            "model": "gemini-1.5-flash",
            "modelConfig": {
                "temperature": 0.3,
                "max_tokens": 1000
            },
            "capabilities": ["test"],
            "tools": [],
            "version": 1,
            "isActive": True,
            "systemPrompt": "You are a helpful test agent.",
            "userPrompt": "Analyze this: {interaction}"
        }
        
        print("\n2. Creating Test Agent:")
        agent = await factory.create_agent(template)
        print(f"   ✓ Created agent: {agent.template['name']}")
        
        # Test agent execution
        print("\n3. Testing Agent Execution:")
        test_input = {
            "interaction": {"content": "Test interaction"},
            "trace_id": "test-trace-001"
        }
        
        result = await agent.analyze(test_input)
        print(f"   ✓ Agent executed successfully")
        print(f"   - Confidence: {result.get('confidence', 0):.2%}")
        print(f"   - Model used: {result.get('model_used', 'unknown')}")
        
        # Cleanup
        await database_manager.disconnect()
        await cache.close()
        
        print("\n" + "=" * 60)
        print("✅ Agent Factory integration test PASSED!")
        print("=" * 60)
        
    except ImportError as e:
        print(f"   ⚠️  Import error (ADK may not be installed): {e}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


async def main():
    """Run all tests"""
    
    # Test basic Gemini configuration
    success = await test_gemini_configuration()
    
    if success:
        # Test Agent Factory integration if Gemini works
        await test_agent_factory_integration()
    
    print("\n📝 Configuration Summary:")
    print(f"   - Google API Key: {'✓ Configured' if (settings.GOOGLE_API_KEY or os.getenv('GOOGLE_API_KEY')) else '✗ Not configured'}")
    print(f"   - OpenAI API Key: {'✓ Configured' if settings.OPENAI_API_KEY else '✗ Not configured (optional)'}")
    print(f"   - Anthropic API Key: {'✓ Configured' if settings.ANTHROPIC_API_KEY else '✗ Not configured (optional)'}")
    
    print("\n💡 Next Steps:")
    if success:
        print("   1. Your Gemini configuration is working!")
        print("   2. You can now run the full orchestration pipeline")
        print("   3. Try: python scripts/test_orchestration.py")
    else:
        print("   1. Add your Google API key to .env file")
        print("   2. Get a key from: https://makersuite.google.com/app/apikey")
        print("   3. Run this test again to verify")


if __name__ == "__main__":
    asyncio.run(main())