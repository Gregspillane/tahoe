#!/usr/bin/env python3
"""Test individual transcription providers to debug issues."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from transcription.assemblyai_client import AssemblyAIClient, AssemblyAIError
from transcription.google_client import GoogleSpeechClient, GoogleSpeechError
from storage.s3_manager import S3Manager, S3ManagerError

async def test_s3_manager():
    """Test S3Manager file operations."""
    print("=== Testing S3Manager ===")
    
    try:
        s3_manager = S3Manager(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "us-east-2")
        )
        
        audio_url = "s3://tahoedev/pending/sample-speech.wav"
        
        # Test validation
        print(f"Validating S3 access to {audio_url}...")
        is_valid = await s3_manager.validate_s3_access(audio_url)
        if is_valid:
            print("✅ S3 file is accessible")
        else:
            print("❌ S3 file is not accessible")
            return False
        
        # Test presigned URL generation
        print("Generating presigned URL...")
        presigned_url = s3_manager.generate_presigned_url(audio_url, expiration_hours=1)
        print(f"✅ Presigned URL generated: {presigned_url[:50]}...")
        
        # Test file download
        print("Testing file download...")
        temp_file = await s3_manager.download_to_temp(audio_url, "test-job")
        print(f"✅ File downloaded to: {temp_file}")
        
        # Get file info
        file_info = s3_manager.get_file_info(audio_url)
        print(f"✅ File info: size={file_info['size']} bytes, content_type={file_info.get('content_type')}")
        
        # Cleanup temp file (but keep path for Google test)
        print("✅ S3Manager test completed successfully")
        
        return True, presigned_url, temp_file
        
    except Exception as e:
        print(f"❌ S3Manager test failed: {e}")
        return False, None, None

async def test_assemblyai(presigned_url):
    """Test AssemblyAI client."""
    print("\n=== Testing AssemblyAI ===")
    
    try:
        client = AssemblyAIClient(os.getenv("ASSEMBLYAI_API_KEY"))
        
        print(f"Testing AssemblyAI with presigned URL...")
        result = await client.transcribe_audio(presigned_url, "test-assemblyai")
        
        print("✅ AssemblyAI transcription successful!")
        print(f"   Transcript: {result.get('transcript', 'N/A')[:100]}...")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ AssemblyAI test failed: {e}")
        return False

async def test_google_speech(temp_file, s3_manager):
    """Test Google Speech client."""
    print("\n=== Testing Google Speech ===")
    
    try:
        client = GoogleSpeechClient(
            project_id=os.getenv("GOOGLE_PROJECT_ID"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="chirp_2",
            language_code="en-US"
        )
        
        # Create a new temp file for this test
        audio_url = "s3://tahoedev/pending/sample-speech.wav"
        print(f"Testing Google Speech with S3 download...")
        result = await client.transcribe_audio(audio_url, "test-google", s3_manager)
        
        print("✅ Google Speech transcription successful!")
        print(f"   Transcript: {result.get('transcript', 'N/A')[:100]}...")
        print(f"   Confidence: {result.get('confidence', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"❌ Google Speech test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("=== Transcription Providers Debug Test ===\n")
    
    # Test S3Manager
    s3_success, presigned_url, temp_file = await test_s3_manager()
    if not s3_success:
        print("\n❌ S3Manager failed - cannot proceed with provider tests")
        return
    
    # Test AssemblyAI
    assemblyai_success = await test_assemblyai(presigned_url)
    
    # Re-create S3 manager for Google test
    s3_manager = S3Manager(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.getenv("AWS_REGION", "us-east-2")
    )
    
    # Test Google Speech  
    google_success = await test_google_speech(temp_file, s3_manager)
    
    print("\n=== Test Results ===")
    print(f"S3Manager: {'✅ OK' if s3_success else '❌ FAILED'}")
    print(f"AssemblyAI: {'✅ OK' if assemblyai_success else '❌ FAILED'}")
    print(f"Google Speech: {'✅ OK' if google_success else '❌ FAILED'}")
    
    if s3_success and assemblyai_success and google_success:
        print("\n🎉 All systems working - parallel processing should work!")
    else:
        print("\n⚠️  Some systems failed - need to debug issues")

if __name__ == "__main__":
    asyncio.run(main())