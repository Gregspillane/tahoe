#!/usr/bin/env python3
"""Test script to verify LLM provider integration works with real API calls"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.registry import ModelRegistry
from models.providers.base import ProviderError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_provider_validation():
    """Test that we can validate API keys"""
    print("\n=== Testing Provider API Key Validation ===")
    
    registry = ModelRegistry()
    results = await registry.validate_providers()
    
    for provider, is_valid in results.items():
        status = "✅ Valid" if is_valid else "❌ Invalid/Missing"
        print(f"{provider}: {status}")
    
    return results


async def test_gemini_generation():
    """Test Gemini provider with real API call"""
    print("\n=== Testing Gemini Generation ===")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set in environment")
        return False
    
    registry = ModelRegistry()
    
    try:
        # Test with a simple prompt
        response = await registry.generate_with_model(
            model_name="gemini-1.5-flash",
            prompt="What is 2+2? Reply with just the number.",
            temperature=0.1
        )
        
        print(f"✅ Gemini response: {response.strip()}")
        return True
        
    except ProviderError as e:
        print(f"❌ Provider error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        await registry.cleanup()


async def test_model_availability():
    """Test checking model availability"""
    print("\n=== Testing Model Availability Check ===")
    
    registry = ModelRegistry()
    
    test_models = [
        "gemini-1.5-flash",
        "gpt-4-turbo",
        "claude-3-sonnet",
        "fake-model-xyz"
    ]
    
    for model in test_models:
        try:
            is_available = await registry.check_model_availability(model)
            status = "✅ Available" if is_available else "❌ Not available"
            print(f"{model}: {status}")
        except Exception as e:
            print(f"{model}: ❌ Error - {e}")
    
    await registry.cleanup()


async def test_compliance_prompt():
    """Test a compliance analysis prompt"""
    print("\n=== Testing Compliance Analysis Prompt ===")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set")
        return False
    
    registry = ModelRegistry()
    
    try:
        # Test with a compliance-focused prompt
        test_transcript = """
        Agent: Hello, this is John from ABC Collections. 
        Customer: How did you get this number?
        Agent: We're calling about your outstanding debt of $5000.
        Customer: I don't owe that much!
        Agent: If you don't pay, we'll contact your employer.
        """
        
        system_prompt = """You are a compliance analyst. Analyze the following call transcript 
        for potential FDCPA violations. List any violations found with brief explanations."""
        
        response = await registry.generate_with_model(
            model_name="gemini-1.5-flash",
            prompt=test_transcript,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        print("✅ Compliance analysis response:")
        print(response[:500] + "..." if len(response) > 500 else response)
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await registry.cleanup()


async def main():
    """Run all tests"""
    print("🚀 Starting LLM Provider Integration Tests")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set in environment")
        print("Please set it in your .env file or environment variables")
        print("Example: export GOOGLE_API_KEY='your-api-key-here'")
    
    # Run tests
    results = []
    
    # Test 1: Validate providers
    validation_results = await test_provider_validation()
    results.append(any(validation_results.values()))
    
    # Test 2: Test Gemini generation
    if validation_results.get("gemini"):
        results.append(await test_gemini_generation())
    
    # Test 3: Model availability
    await test_model_availability()
    
    # Test 4: Compliance prompt
    if validation_results.get("gemini"):
        results.append(await test_compliance_prompt())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)