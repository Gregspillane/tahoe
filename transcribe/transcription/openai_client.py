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
from storage.s3_helper import S3Helper

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
        
    async def transcribe_audio(self, audio_url: str, job_id: str) -> Dict[str, Any]:
        """
        Complete transcription workflow using OpenAI gpt-4o-transcribe.
        
        Args:
            audio_url: S3 URL or local file path to audio
            job_id: Unique job identifier for tracking
            
        Returns:
            Dict containing transcription results and metadata
        """
        logger.info(f"Starting OpenAI transcription for job {job_id}")
        
        try:
            # Step 1: Download audio file if it's an S3 URL
            local_file_path = await self._prepare_audio_file(audio_url, job_id)
            
            # Step 2: Validate file size and format
            await self._validate_audio_file(local_file_path)
            
            # Step 3: Submit transcription request
            transcript_data = await self._transcribe_file(local_file_path, job_id)
            
            # Step 4: Format results
            result = self._format_transcript_result(transcript_data, job_id)
            
            # Step 5: Cleanup temporary file if we downloaded it
            if audio_url.startswith(('s3://', 'http')):
                await self._cleanup_temp_file(local_file_path)
            
            logger.info(f"OpenAI transcription completed for job {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI transcription failed for job {job_id}: {e}")
            raise OpenAIError(f"Transcription failed: {str(e)}") from e
    
    async def _prepare_audio_file(self, audio_url: str, job_id: str) -> str:
        """Download audio file if needed and return local path."""
        
        # If it's already a local file, return as-is
        if not audio_url.startswith(('s3://', 'http')):
            if os.path.exists(audio_url):
                return audio_url
            else:
                raise OpenAIError(f"Local file not found: {audio_url}")
        
        # For S3 or HTTP URLs, we need to download
        logger.info(f"Downloading audio file for job {job_id}: {audio_url}")
        
        try:
            # Create temp directory if it doesn't exist
            temp_dir = Path("/tmp/transcription")
            temp_dir.mkdir(exist_ok=True)
            
            # Generate temp file name
            file_extension = self._get_file_extension(audio_url)
            temp_file_path = temp_dir / f"{job_id}{file_extension}"
            
            # Download file
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                # Write to temp file
                with open(temp_file_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Audio file downloaded: {temp_file_path}")
                return str(temp_file_path)
                
        except Exception as e:
            logger.error(f"Failed to download audio file: {e}")
            raise OpenAIError(f"Audio download failed: {str(e)}")
    
    def _get_file_extension(self, url: str) -> str:
        """Extract file extension from URL or default to .mp3."""
        try:
            path = Path(url)
            extension = path.suffix.lower()
            
            # Supported formats by OpenAI
            supported = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
            if extension in supported:
                return extension
            else:
                # Default to .mp3 if we can't determine
                return '.mp3'
        except:
            return '.mp3'
    
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
    
    async def _cleanup_temp_file(self, file_path: str) -> None:
        """Remove temporary downloaded file."""
        try:
            if os.path.exists(file_path) and "/tmp/transcription" in file_path:
                os.unlink(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def _format_transcript_result(self, transcript_data: Dict[str, Any], job_id: str) -> Dict[str, Any]:
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
        
        # Format result to match AssemblyAI structure
        result = {
            "provider": "openai",
            "job_id": job_id,
            "transcript_id": f"openai_{job_id}",  # Generate ID since OpenAI doesn't provide one
            "transcript_text": transcript_text,
            "confidence": confidence,
            "duration": duration,
            "segments": segments,  # OpenAI provides segments instead of speakers
            "words": words,
            "chapters": [],  # OpenAI doesn't provide chapters
            "sentiment_analysis": [],  # OpenAI doesn't provide sentiment
            "entities": [],  # OpenAI doesn't provide entities
            "processing_time": duration,  # Placeholder
            "metadata": {
                "language": transcript_data.get("language"),
                "model": self.model,
                "task": transcript_data.get("task", "transcribe"),
                "timestamp_granularities": ["word", "segment"]
            },
            "raw_response": transcript_data  # Keep full response for debugging
        }
        
        logger.info(f"Formatted OpenAI result for job {job_id}: {len(transcript_text)} chars, {confidence:.2f} confidence")
        return result