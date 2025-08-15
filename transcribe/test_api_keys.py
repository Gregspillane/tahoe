#!/usr/bin/env python3
"""Test script to verify API keys work directly."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_assemblyai():
    """Test AssemblyAI API key."""
    print("Testing AssemblyAI API key...")
    try:
        import httpx
        
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            print("❌ AssemblyAI API key not found in environment")
            return False
            
        # Test with a simple API call to check authentication
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.assemblyai.com/v2/account",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                print("✅ AssemblyAI API key is valid")
                return True
            else:
                print(f"❌ AssemblyAI API key failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ AssemblyAI test error: {e}")
        return False

async def test_google_speech():
    """Test Google Cloud Speech API credentials."""
    print("Testing Google Cloud Speech credentials...")
    try:
        import httpx
        import os
        
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not project_id:
            print("❌ GOOGLE_PROJECT_ID not found in environment")
            return False
            
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        # Test Google Speech API with a simple recognition config test
        # Use REST API endpoint to validate API key
        async with httpx.AsyncClient() as client:
            url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
            
            # Test payload (empty audio, just to validate credentials)
            test_payload = {
                "config": {
                    "encoding": "LINEAR16",
                    "sampleRateHertz": 16000,
                    "languageCode": "en-US",
                },
                "audio": {
                    "content": ""  # Empty content for testing
                }
            }
            
            response = await client.post(url, json=test_payload)
            
            # We expect a 400 error for empty audio, but that means credentials work
            if response.status_code == 400:
                error_data = response.json()
                if "INVALID_ARGUMENT" in str(error_data):
                    print("✅ Google Cloud Speech API key is valid")
                    print(f"✅ Project ID: {project_id}")
                    return True
            elif response.status_code == 403:
                print(f"❌ Google API key authentication failed: {response.text}")
                return False
            elif response.status_code == 200:
                print("✅ Google Cloud Speech API key is valid")
                print(f"✅ Project ID: {project_id}")
                return True
            else:
                print(f"❌ Unexpected response: {response.status_code} - {response.text}")
                return False
        
    except Exception as e:
        print(f"❌ Google Speech test error: {e}")
        return False

async def main():
    """Main test function."""
    print("=== API Key Validation Test ===")
    
    assemblyai_ok = await test_assemblyai()
    google_ok = await test_google_speech()
    
    print("\n=== Results ===")
    print(f"AssemblyAI: {'✅ OK' if assemblyai_ok else '❌ FAILED'}")
    print(f"Google Speech: {'✅ OK' if google_ok else '❌ FAILED'}")
    
    if assemblyai_ok and google_ok:
        print("\n🎉 All API credentials are valid!")
    else:
        print("\n⚠️  Some API credentials failed - check your .env file and Google credentials")

if __name__ == "__main__":
    asyncio.run(main())