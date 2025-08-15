"""
AssemblyAI client implementation for the Transcription Service.
Handles audio upload, transcription requests, and result polling.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import httpx
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AssemblyAIError(Exception):
    """Custom exception for AssemblyAI API errors."""
    pass


class AssemblyAIClient:
    """Async client for AssemblyAI transcription service."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.assemblyai.com/v2"
        self.upload_url = "https://api.assemblyai.com/v2/upload"
        
        # Client configuration
        self.timeout = httpx.Timeout(60.0)  # 60 second timeout for API calls
        self.poll_interval = 5  # seconds between status polls
        self.max_poll_duration = 1800  # 30 minutes max polling
        
        # Headers for API requests
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }
        
    async def transcribe_audio(self, audio_url: str, job_id: str) -> Dict[str, Any]:
        """
        Complete transcription workflow: upload if needed, submit, poll for results.
        
        Args:
            audio_url: S3 URL or local file path to audio
            job_id: Unique job identifier for tracking
            
        Returns:
            Dict containing transcription results and metadata
        """
        logger.info(f"Starting AssemblyAI transcription for job {job_id}")
        
        try:
            # Step 1: Upload audio if it's a local file, or use S3 URL directly
            if audio_url.startswith('s3://') or audio_url.startswith('http'):
                upload_url = audio_url
            else:
                upload_url = await self._upload_audio(audio_url)
            
            # Step 2: Submit transcription request
            transcript_id = await self._submit_transcription(upload_url, job_id)
            
            # Step 3: Poll for results
            transcript_data = await self._poll_for_results(transcript_id, job_id)
            
            # Step 4: Extract and format results
            result = self._format_transcript_result(transcript_data, job_id)
            
            logger.info(f"AssemblyAI transcription completed for job {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed for job {job_id}: {e}")
            raise AssemblyAIError(f"Transcription failed: {str(e)}") from e
    
    async def _upload_audio(self, file_path: str) -> str:
        """Upload audio file to AssemblyAI and return upload URL."""
        logger.info(f"Uploading audio file: {file_path}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Read file and upload
                with open(file_path, 'rb') as audio_file:
                    upload_headers = {"authorization": self.api_key}
                    
                    response = await client.post(
                        self.upload_url,
                        headers=upload_headers,
                        files={"file": audio_file}
                    )
                    response.raise_for_status()
                    
                    upload_data = response.json()
                    upload_url = upload_data.get("upload_url")
                    
                    if not upload_url:
                        raise AssemblyAIError("No upload URL returned from AssemblyAI")
                    
                    logger.info(f"Audio file uploaded successfully: {upload_url}")
                    return upload_url
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during upload: {e.response.status_code} - {e.response.text}")
            raise AssemblyAIError(f"Upload failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise AssemblyAIError(f"Upload failed: {str(e)}")
    
    async def _submit_transcription(self, audio_url: str, job_id: str) -> str:
        """Submit transcription request to AssemblyAI."""
        logger.info(f"Submitting transcription request for job {job_id}")
        
        # Configure transcription options for compliance/call center use
        transcription_config = {
            "audio_url": audio_url,
            "speaker_labels": True,  # Enable speaker diarization
            "speakers_expected": 2,   # Typical for calls (can be adjusted)
            "auto_chapters": True,    # Segment conversation into topics
            "sentiment_analysis": True,  # Analyze sentiment
            "entity_detection": True,    # Detect names, numbers, dates
            "iab_categories": False,     # Skip content categorization for calls
            "content_safety": False,     # Skip content safety for business calls
            "auto_highlights": False,    # Skip highlights for transcripts
            "punctuate": True,
            "format_text": True,
            "dual_channel": False,  # Set to True if stereo audio with separate channels
            "webhook_url": None,    # Use polling instead of webhooks for MVP
            "word_boost": [],       # Could add domain-specific terms later
            "boost_param": "default"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/transcript",
                    headers=self.headers,
                    json=transcription_config
                )
                response.raise_for_status()
                
                submit_data = response.json()
                transcript_id = submit_data.get("id")
                
                if not transcript_id:
                    raise AssemblyAIError("No transcript ID returned from AssemblyAI")
                
                logger.info(f"Transcription submitted successfully for job {job_id}, transcript_id: {transcript_id}")
                return transcript_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during submission: {e.response.status_code} - {e.response.text}")
            raise AssemblyAIError(f"Submission failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Submission error: {e}")
            raise AssemblyAIError(f"Submission failed: {str(e)}")
    
    async def _poll_for_results(self, transcript_id: str, job_id: str) -> Dict[str, Any]:
        """Poll AssemblyAI for transcription results."""
        logger.info(f"Polling for results: job {job_id}, transcript_id {transcript_id}")
        
        start_time = datetime.now()
        max_end_time = start_time + timedelta(seconds=self.max_poll_duration)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                while datetime.now() < max_end_time:
                    response = await client.get(
                        f"{self.base_url}/transcript/{transcript_id}",
                        headers=self.headers
                    )
                    response.raise_for_status()
                    
                    transcript_data = response.json()
                    status = transcript_data.get("status")
                    
                    logger.debug(f"Polling status for job {job_id}: {status}")
                    
                    if status == "completed":
                        logger.info(f"Transcription completed for job {job_id}")
                        return transcript_data
                    elif status == "error":
                        error_msg = transcript_data.get("error", "Unknown error")
                        raise AssemblyAIError(f"Transcription failed: {error_msg}")
                    elif status in ["queued", "processing"]:
                        # Still processing, wait and poll again
                        await asyncio.sleep(self.poll_interval)
                        continue
                    else:
                        raise AssemblyAIError(f"Unknown status: {status}")
                
                # Timeout reached
                raise AssemblyAIError(f"Polling timeout after {self.max_poll_duration} seconds")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during polling: {e.response.status_code} - {e.response.text}")
            raise AssemblyAIError(f"Polling failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Polling error: {e}")
            raise AssemblyAIError(f"Polling failed: {str(e)}")
    
    def _format_transcript_result(self, transcript_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
        """Format AssemblyAI response into standardized result structure."""
        
        # Extract core transcript
        transcript_text = transcript_data.get("text", "")
        confidence = transcript_data.get("confidence", 0.0)
        
        # Extract speaker diarization
        speakers = []
        utterances = transcript_data.get("utterances", []) or []
        for utterance in utterances:
            speakers.append({
                "speaker": utterance.get("speaker"),
                "text": utterance.get("text"),
                "start": utterance.get("start"),
                "end": utterance.get("end"),
                "confidence": utterance.get("confidence", 0.0)
            })
        
        # Extract words with timestamps
        words = []
        word_data = transcript_data.get("words", []) or []
        for word in word_data:
            words.append({
                "text": word.get("text"),
                "start": word.get("start"),
                "end": word.get("end"),
                "confidence": word.get("confidence", 0.0),
                "speaker": word.get("speaker")
            })
        
        # Extract chapters/topics
        chapters = []
        chapter_data = transcript_data.get("chapters", []) or []
        for chapter in chapter_data:
            chapters.append({
                "gist": chapter.get("gist"),
                "headline": chapter.get("headline"),
                "summary": chapter.get("summary"),
                "start": chapter.get("start"),
                "end": chapter.get("end")
            })
        
        # Extract sentiment analysis
        sentiment_data = transcript_data.get("sentiment_analysis_results", [])
        
        # Extract entities
        entities = transcript_data.get("entities", [])
        
        # Format result
        result = {
            "provider": "assemblyai",
            "job_id": job_id,
            "transcript_id": transcript_data.get("id"),
            "transcript_text": transcript_text,
            "confidence": confidence,
            "duration": transcript_data.get("audio_duration", 0),
            "speakers": speakers,
            "words": words,
            "chapters": chapters,
            "sentiment_analysis": sentiment_data,
            "entities": entities,
            "processing_time": transcript_data.get("audio_duration", 0),  # Placeholder
            "metadata": {
                "language_code": transcript_data.get("language_code"),
                "audio_url": transcript_data.get("audio_url"),
                "status": transcript_data.get("status"),
                "created": transcript_data.get("created"),
                "completed": transcript_data.get("completed")
            },
            "raw_response": transcript_data  # Keep full response for debugging
        }
        
        logger.info(f"Formatted AssemblyAI result for job {job_id}: {len(transcript_text)} chars, {confidence:.2f} confidence")
        return result