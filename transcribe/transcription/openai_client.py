"""
OpenAI client implementation for the Transcription Service.
Handles audio transcription using gpt-4o-transcribe model.
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
import httpx
import os
from pathlib import Path
from storage.s3_manager import S3Manager, S3ManagerError

logger = logging.getLogger(__name__)


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass


class OpenAIClient:
    """Async client for OpenAI transcription service using gpt-4o-transcribe."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-transcribe"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
        
        # Client configuration
        self.timeout = httpx.Timeout(120.0)  # 2 minutes for transcription
        self.max_file_size = 25 * 1024 * 1024  # 25MB OpenAI limit
        
        # Headers for API requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
    async def transcribe_audio(self, audio_url: str, job_id: str, s3_manager: S3Manager) -> Dict[str, Any]:
        """
        Complete transcription workflow using OpenAI gpt-4o-transcribe.
        
        Args:
            audio_url: S3 URL to audio file
            job_id: Unique job identifier for tracking
            s3_manager: S3Manager instance for file operations
            
        Returns:
            Dict containing transcription results and metadata
        """
        logger.info(f"Starting OpenAI transcription for job {job_id}")
        
        temp_file_path = None
        try:
            # Step 1: Download audio file from S3
            temp_file_path = await s3_manager.download_to_temp(audio_url, job_id)
            
            # Step 2: Validate file size and format
            await self._validate_audio_file(temp_file_path)
            
            # Step 3: Submit transcription request
            transcript_data = await self._transcribe_file(temp_file_path, job_id)
            
            # Step 4: Format results
            result = self._format_transcript_result(transcript_data, job_id, audio_url)
            
            logger.info(f"OpenAI transcription completed for job {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI transcription failed for job {job_id}: {e}")
            raise OpenAIError(f"Transcription failed: {str(e)}") from e
        
        finally:
            # Cleanup temporary file
            if temp_file_path:
                await s3_manager.cleanup_temp_file(temp_file_path)
    
    
    async def _validate_audio_file(self, file_path: str) -> None:
        """Validate audio file size and format."""
        try:
            file_size = os.path.getsize(file_path)
            
            if file_size > self.max_file_size:
                raise OpenAIError(f"File too large: {file_size} bytes (max {self.max_file_size})")
            
            # Check file extension
            extension = Path(file_path).suffix.lower()
            supported_formats = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
            
            if extension not in supported_formats:
                logger.warning(f"Unsupported file format: {extension}, trying anyway")
            
            logger.debug(f"Audio file validated: {file_path} ({file_size} bytes)")
            
        except Exception as e:
            logger.error(f"Audio file validation failed: {e}")
            raise OpenAIError(f"File validation failed: {str(e)}")
    
    async def _transcribe_file(self, file_path: str, job_id: str) -> Dict[str, Any]:
        """Submit file to OpenAI for transcription."""
        logger.info(f"Submitting transcription to OpenAI for job {job_id}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare the file for upload
                with open(file_path, 'rb') as audio_file:
                    files = {
                        'file': (Path(file_path).name, audio_file, 'audio/mpeg')
                    }
                    
                    # Transcription parameters
                    data = {
                        'model': self.model,
                        'response_format': 'verbose_json',  # Include timestamps and confidence
                        'timestamp_granularities[]': ['word', 'segment'],  # Word and segment level timestamps
                        'language': None,  # Auto-detect language
                    }
                    
                    # Submit request
                    response = await client.post(
                        f"{self.base_url}/audio/transcriptions",
                        headers=self.headers,
                        files=files,
                        data=data
                    )
                    response.raise_for_status()
                    
                    transcript_data = response.json()
                    logger.info(f"OpenAI transcription completed for job {job_id}")
                    return transcript_data
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during transcription: {e.response.status_code} - {e.response.text}")
            raise OpenAIError(f"Transcription failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise OpenAIError(f"Transcription failed: {str(e)}")
    
    
    def _format_transcript_result(self, transcript_data: Dict[str, Any], job_id: str, audio_url: str) -> Dict[str, Any]:
        """Format OpenAI response into standardized result structure."""
        
        # Extract core transcript
        transcript_text = transcript_data.get("text", "")
        
        # Extract segments with timestamps
        segments = []
        segments_data = transcript_data.get("segments", [])
        for segment in segments_data:
            segments.append({
                "text": segment.get("text", "").strip(),
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "avg_logprob": segment.get("avg_logprob", 0.0),
                "compression_ratio": segment.get("compression_ratio", 0.0),
                "no_speech_prob": segment.get("no_speech_prob", 0.0),
                "temperature": segment.get("temperature", 0.0)
            })
        
        # Extract words with timestamps
        words = []
        words_data = transcript_data.get("words", [])
        for word in words_data:
            words.append({
                "text": word.get("word", "").strip(),
                "start": word.get("start", 0),
                "end": word.get("end", 0),
                "probability": word.get("probability", 0.0)
            })
        
        # Calculate overall confidence from word probabilities
        if words:
            confidence = sum(word.get("probability", 0.0) for word in words_data) / len(words_data)
        else:
            # Fall back to segment average log probability
            if segments_data:
                # Convert log prob to approximate confidence (this is an approximation)
                avg_logprob = sum(seg.get("avg_logprob", -1.0) for seg in segments_data) / len(segments_data)
                confidence = max(0.0, min(1.0, (avg_logprob + 1.0)))  # Rough conversion
            else:
                confidence = 0.0
        
        # Calculate duration from segments
        duration = 0
        if segments_data:
            duration = max(seg.get("end", 0) for seg in segments_data)
        
        # Format result to match the expected provider structure
        result = {
            "job_id": job_id,
            "audio_url": audio_url,
            "provider": "openai",
            "model": self.model,
            "language": transcript_data.get("language", "en"),
            "status": "completed",
            "transcript": transcript_text,
            "confidence": confidence,
            "words": words,
            "segments": segments,
            "word_count": len(transcript_text.split()) if transcript_text else 0,
            "duration": duration,
            "metadata": {
                "processing_time": datetime.utcnow().isoformat(),
                "model_version": self.model,
                "api_version": "v1",
                "language": transcript_data.get("language"),
                "task": transcript_data.get("task", "transcribe")
            }
        }
        
        logger.info(f"Formatted OpenAI result for job {job_id}: {len(transcript_text)} chars, {confidence:.2f} confidence")
        return result