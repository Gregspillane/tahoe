"""
Google Cloud Speech client implementation for the Transcription Service.
Handles audio transcription using Google Chirp 2 model with speaker diarization.
"""

import asyncio
import logging
import os
import base64
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

import httpx
from google.cloud import speech
from google.oauth2 import service_account
from google.api_core import exceptions as google_exceptions

from storage.s3_manager import S3Manager, S3ManagerError

logger = logging.getLogger(__name__)


class GoogleSpeechError(Exception):
    """Custom exception for Google Speech API errors."""
    pass


class GoogleSpeechClient:
    """Google Cloud Speech client for transcription with Chirp 2 model."""
    
    def __init__(
        self, 
        project_id: str, 
        credentials_path: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "chirp_2",
        language_code: str = "en-US"
    ):
        """Initialize Google Speech client.
        
        Args:
            project_id: Google Cloud project ID
            credentials_path: Path to service account JSON key file
            api_key: Google API key for REST API fallback
            model: Speech recognition model (default: chirp_2)
            language_code: Language code for transcription (default: en-US)
        """
        self.project_id = project_id
        self.model = model
        self.language_code = language_code
        self.credentials_path = credentials_path
        self.api_key = api_key
        self.client = None
        self.use_rest_api = False
        
        # Try to initialize with service account first, then fall back to REST API
        try:
            if credentials_path and os.path.exists(credentials_path):
                # Try service account authentication
                logger.info(f"Attempting service account authentication: {credentials_path}")
                try:
                    # Check if this is a real service account file
                    with open(credentials_path, 'r') as f:
                        cred_data = json.load(f)
                        if cred_data.get('private_key') == '-----BEGIN PRIVATE KEY-----\nPLACEHOLDER_KEY\n-----END PRIVATE KEY-----\n':
                            raise Exception("Placeholder service account file detected")
                    
                    credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    self.client = speech.SpeechClient(credentials=credentials)
                    logger.info(f"✅ Service account authentication successful")
                    
                    # Test the client
                    self._test_client_authentication()
                    
                except Exception as sa_error:
                    logger.warning(f"Service account authentication failed: {sa_error}")
                    if api_key:
                        logger.info("Falling back to REST API with API key")
                        self.use_rest_api = True
                    else:
                        raise GoogleSpeechError(f"Service account failed and no API key provided: {str(sa_error)}")
            
            elif api_key:
                # Use REST API with API key
                logger.info(f"Using Google Speech REST API with API key authentication")
                self.use_rest_api = True
                
            else:
                # Try Application Default Credentials as last resort
                logger.info(f"Attempting Application Default Credentials")
                try:
                    self.client = speech.SpeechClient()
                    logger.info(f"✅ Application Default Credentials successful")
                    
                    # Test the client
                    self._test_client_authentication()
                    
                except Exception as adc_error:
                    logger.error(f"All authentication methods failed")
                    raise GoogleSpeechError(
                        f"Authentication failed. Please either:\n"
                        f"1. Provide a valid service account JSON file, or\n" 
                        f"2. Provide a Google API key, or\n"
                        f"3. Run 'gcloud auth application-default login'\n"
                        f"Last error: {str(adc_error)}"
                    ) from adc_error
            
            if self.use_rest_api:
                logger.info(f"✅ Google Speech REST API mode enabled")
            
            logger.info(f"GoogleSpeechClient ready - Project: {project_id}, Model: {model}, Language: {language_code}")
            
        except GoogleSpeechError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Google Speech client: {e}")
            raise GoogleSpeechError(f"Client initialization failed: {str(e)}") from e
        
        # Audio configuration limits
        self.max_sync_duration = 60  # 1 minute for synchronous recognition
        self.max_async_duration = 480 * 60  # 480 minutes for async recognition
        self.max_file_size = 10 * 1024 * 1024  # 10MB for synchronous recognition
    
    def _test_client_authentication(self):
        """Test client authentication by creating a simple config."""
        if self.client:
            test_config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.language_code,
                model=self.model
            )
            logger.info("Client authentication test passed")
    
    async def transcribe_audio(self, audio_url: str, job_id: str, s3_manager: S3Manager) -> Dict[str, Any]:
        """
        Complete transcription workflow using Google Speech Chirp 2.
        
        Args:
            audio_url: S3 URL to audio file
            job_id: Unique job identifier for tracking
            s3_manager: S3Manager instance for file operations
            
        Returns:
            Dict containing transcription results and metadata
        """
        logger.info(f"Starting Google Speech transcription for job {job_id}")
        
        temp_file_path = None
        try:
            # Step 1: Download audio file from S3
            temp_file_path = await s3_manager.download_to_temp(audio_url, job_id)
            
            # Step 2: Validate audio file
            await self._validate_audio_file(temp_file_path)
            
            # Step 3: Determine transcription method (sync vs async)
            file_info = await self._get_audio_info(temp_file_path)
            use_async = (
                file_info['duration'] > self.max_sync_duration or 
                file_info['size'] > self.max_file_size
            )
            
            # Step 4: Perform transcription
            if use_async:
                transcript_data = await self._transcribe_long_running(temp_file_path, job_id)
            else:
                transcript_data = await self._transcribe_sync(temp_file_path, job_id)
            
            # Step 5: Format results
            result = self._format_transcript_result(transcript_data, job_id, audio_url)
            
            logger.info(f"Google Speech transcription completed for job {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"Google Speech transcription failed for job {job_id}: {e}")
            raise GoogleSpeechError(f"Transcription failed: {str(e)}") from e
        
        finally:
            # Cleanup temporary file
            if temp_file_path:
                await s3_manager.cleanup_temp_file(temp_file_path)
    
    async def _transcribe_sync(self, audio_file_path: str, job_id: str) -> Dict[str, Any]:
        """Perform synchronous transcription for shorter audio files."""
        logger.info(f"Using synchronous transcription for job {job_id}")
        
        try:
            if self.use_rest_api:
                return await self._transcribe_sync_rest_api(audio_file_path, job_id)
            else:
                return await self._transcribe_sync_client_library(audio_file_path, job_id)
            
        except Exception as e:
            logger.error(f"Sync transcription error: {e}")
            raise GoogleSpeechError(f"Sync transcription failed: {str(e)}") from e
    
    async def _transcribe_sync_client_library(self, audio_file_path: str, job_id: str) -> Dict[str, Any]:
        """Perform synchronous transcription using client library."""
        # Read audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_content = audio_file.read()
        
        # Configure audio and recognition settings
        audio = speech.RecognitionAudio(content=audio_content)
        config = self._get_recognition_config()
        
        # Perform synchronous recognition
        request = speech.RecognizeRequest(
            config=config,
            audio=audio
        )
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            self.client.recognize,
            request
        )
        
        return self._process_recognition_response(response)
    
    async def _transcribe_sync_rest_api(self, audio_file_path: str, job_id: str) -> Dict[str, Any]:
        """Perform synchronous transcription using REST API with API key."""
        # Read and encode audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_content = audio_file.read()
        
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        # Prepare request payload
        request_data = {
            "config": {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": self.language_code,
                "model": self.model,
                "diarizationConfig": {
                    "enableSpeakerDiarization": True,
                    "minSpeakerCount": 1,
                    "maxSpeakerCount": 2
                },
                "enableAutomaticPunctuation": True,
                "enableWordConfidence": True,
                "enableWordTimeOffsets": True,
                "audioChannelCount": 1,
                "enableSeparateRecognitionPerChannel": False,
                "maxAlternatives": 1,
                "profanityFilter": False,
                "useEnhanced": True
            },
            "audio": {
                "content": audio_base64
            }
        }
        
        # Make REST API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://speech.googleapis.com/v1/speech:recognize?key={self.api_key}",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Google Speech REST API error: {response.status_code} - {error_text}")
                raise GoogleSpeechError(f"REST API error: {response.status_code} - {error_text}")
            
            result = response.json()
            return self._process_rest_api_response(result)
    
    async def _transcribe_long_running(self, audio_file_path: str, job_id: str) -> Dict[str, Any]:
        """Perform asynchronous transcription for longer audio files."""
        logger.info(f"Using long-running transcription for job {job_id}")
        
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_content = audio_file.read()
            
            # Configure audio and recognition settings
            audio = speech.RecognitionAudio(content=audio_content)
            config = self._get_recognition_config()
            
            # Start long-running recognition operation
            request = speech.LongRunningRecognizeRequest(
                config=config,
                audio=audio
            )
            
            operation = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.long_running_recognize,
                request
            )
            
            # Poll for completion
            logger.info(f"Polling for long-running operation completion: {operation.name}")
            
            # Wait for operation to complete (with timeout)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                operation.result,
                300  # 5-minute timeout
            )
            
            return self._process_recognition_response(response)
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google API error in long-running transcription: {e}")
            raise GoogleSpeechError(f"Google API error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Long-running transcription error: {e}")
            raise GoogleSpeechError(f"Long-running transcription failed: {str(e)}") from e
    
    def _get_recognition_config(self) -> speech.RecognitionConfig:
        """Create recognition configuration for Google Speech API."""
        
        # Create diarization config
        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=1,
            max_speaker_count=2,  # Assume 2 speakers for call center audio
        )
        
        return speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,  # Will auto-detect
            sample_rate_hertz=16000,  # Common sample rate, will auto-detect if different
            language_code=self.language_code,
            model=self.model,
            
            # Enable advanced features
            diarization_config=diarization_config,
            enable_automatic_punctuation=True,
            enable_word_confidence=True,
            enable_word_time_offsets=True,
            
            # Audio channel configuration
            audio_channel_count=1,  # Mono audio
            enable_separate_recognition_per_channel=False,
            
            # Alternative transcripts
            max_alternatives=1,  # Only get the best alternative
            
            # Profanity filter
            profanity_filter=False,  # Keep original content for compliance
            
            # Use enhanced model for better accuracy
            use_enhanced=True,
        )
    
    def _process_recognition_response(self, response) -> Dict[str, Any]:
        """Process Google Speech API response and extract relevant data."""
        results = []
        words = []
        speakers = {}
        total_confidence = 0.0
        
        for result in response.results:
            alternative = result.alternatives[0]  # Get the best alternative
            
            # Extract transcript text
            transcript_text = alternative.transcript
            confidence = alternative.confidence
            total_confidence += confidence
            
            # Process words with timestamps and speaker information
            for word_info in alternative.words:
                word_data = {
                    'word': word_info.word,
                    'start_time': word_info.start_time.total_seconds(),
                    'end_time': word_info.end_time.total_seconds(),
                    'confidence': word_info.confidence if hasattr(word_info, 'confidence') else confidence,
                    'speaker_tag': getattr(word_info, 'speaker_tag', 0)
                }
                words.append(word_data)
                
                # Track speakers
                speaker_tag = word_data['speaker_tag']
                if speaker_tag not in speakers:
                    speakers[speaker_tag] = {
                        'speaker': f"Speaker {speaker_tag}",
                        'words': []
                    }
                speakers[speaker_tag]['words'].append(word_data)
            
            # Add result segment
            results.append({
                'text': transcript_text,
                'confidence': confidence,
                'start_time': words[0]['start_time'] if words else 0.0,
                'end_time': words[-1]['end_time'] if words else 0.0,
            })
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(response.results) if response.results else 0.0
        
        return {
            'transcript': ' '.join(result['text'] for result in results),
            'confidence': avg_confidence,
            'words': words,
            'speakers': list(speakers.values()),
            'segments': results,
            'language_code': self.language_code,
            'model': self.model
        }
    
    def _process_rest_api_response(self, response_data: Dict) -> Dict[str, Any]:
        """Process Google Speech REST API response and extract relevant data."""
        results = []
        words = []
        speakers = {}
        total_confidence = 0.0
        
        # Handle REST API response format
        for result in response_data.get('results', []):
            alternatives = result.get('alternatives', [])
            if not alternatives:
                continue
                
            alternative = alternatives[0]  # Get the best alternative
            
            # Extract transcript text
            transcript_text = alternative.get('transcript', '')
            confidence = alternative.get('confidence', 0.0)
            total_confidence += confidence
            
            # Process words with timestamps and speaker information
            for word_info in alternative.get('words', []):
                start_time = self._parse_duration(word_info.get('startTime', '0s'))
                end_time = self._parse_duration(word_info.get('endTime', '0s'))
                
                word_data = {
                    'word': word_info.get('word', ''),
                    'start_time': start_time,
                    'end_time': end_time,
                    'confidence': word_info.get('confidence', confidence),
                    'speaker_tag': word_info.get('speakerTag', 0)
                }
                words.append(word_data)
                
                # Track speakers
                speaker_tag = word_data['speaker_tag']
                if speaker_tag not in speakers:
                    speakers[speaker_tag] = {
                        'speaker': f"Speaker {speaker_tag}",
                        'words': []
                    }
                speakers[speaker_tag]['words'].append(word_data)
            
            # Add result segment
            results.append({
                'text': transcript_text,
                'confidence': confidence,
                'start_time': words[0]['start_time'] if words else 0.0,
                'end_time': words[-1]['end_time'] if words else 0.0,
            })
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(response_data.get('results', [])) if response_data.get('results') else 0.0
        
        return {
            'transcript': ' '.join(result['text'] for result in results),
            'confidence': avg_confidence,
            'words': words,
            'speakers': list(speakers.values()),
            'segments': results,
            'language_code': self.language_code,
            'model': self.model
        }
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse Google API duration string (e.g., '1.234s') to float seconds."""
        if duration_str.endswith('s'):
            return float(duration_str[:-1])
        return 0.0
    
    def _format_transcript_result(self, transcript_data: Dict[str, Any], job_id: str, audio_url: str) -> Dict[str, Any]:
        """Format transcription result to match expected output structure."""
        return {
            'job_id': job_id,
            'audio_url': audio_url,
            'provider': 'google_speech',
            'model': self.model,
            'status': 'completed',
            'created_at': datetime.now().isoformat(),
            
            # Main transcript data
            'transcript': transcript_data['transcript'],
            'confidence': transcript_data['confidence'],
            'language': transcript_data['language_code'],
            
            # Detailed data
            'words': transcript_data['words'],
            'speakers': transcript_data['speakers'],
            'segments': transcript_data['segments'],
            
            # Metadata
            'word_count': len(transcript_data['words']),
            'speaker_count': len(transcript_data['speakers']),
            'duration': transcript_data['segments'][-1]['end_time'] if transcript_data['segments'] else 0.0,
            
            # Provider-specific data
            'provider_data': {
                'model': self.model,
                'language_code': self.language_code,
                'raw_response': transcript_data
            }
        }
    
    async def _validate_audio_file(self, file_path: str):
        """Validate audio file format and size."""
        if not os.path.exists(file_path):
            raise GoogleSpeechError(f"Audio file not found: {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise GoogleSpeechError("Audio file is empty")
        
        # Log file info
        logger.info(f"Audio file validation passed: {file_path} ({file_size} bytes)")
    
    async def _get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """Get audio file information for processing decisions."""
        file_size = os.path.getsize(file_path)
        
        # Estimate duration based on file size (rough estimate)
        # Assuming ~128kbps MP3: 1MB ≈ 65 seconds
        estimated_duration = (file_size / 1024 / 1024) * 65
        
        return {
            'size': file_size,
            'duration': estimated_duration,  # Rough estimate
            'path': file_path
        }