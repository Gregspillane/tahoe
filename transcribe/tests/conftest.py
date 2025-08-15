"""
PyTest configuration and shared fixtures for transcription service testing.
"""

import pytest
import json
from typing import Dict, Any


@pytest.fixture
def sample_assemblyai_response() -> Dict[str, Any]:
    """Sample AssemblyAI API response for testing."""
    return {
        "provider": "assemblyai",
        "job_id": "test-job-001",
        "text": "Hello, this is Hunt and Henriquez law firm. How can we help you today?",
        "confidence": 0.95,
        "duration": 3500,
        "word_count": 12,
        "words": [
            {"text": "Hello", "confidence": 0.98, "start": 0, "end": 500},
            {"text": "this", "confidence": 0.97, "start": 500, "end": 700},
            {"text": "is", "confidence": 0.99, "start": 700, "end": 800},
            {"text": "Hunt", "confidence": 0.95, "start": 800, "end": 1000},
            {"text": "and", "confidence": 0.98, "start": 1000, "end": 1100},
            {"text": "Henriquez", "confidence": 0.85, "start": 1100, "end": 1500},
            {"text": "law", "confidence": 0.97, "start": 1500, "end": 1700},
            {"text": "firm", "confidence": 0.96, "start": 1700, "end": 1900}
        ]
    }


@pytest.fixture
def sample_openai_response() -> Dict[str, Any]:
    """Sample OpenAI API response for testing."""
    return {
        "provider": "openai",
        "job_id": "test-job-001",
        "text": "Hello, this is Hunt & Henriques law firm. How can we help you today?",
        "confidence": 0.92,
        "duration": 3500,
        "word_count": 12,
        "segments": [
            {
                "text": "Hello, this is Hunt & Henriques law firm.",
                "start": 0,
                "end": 2000,
                "avg_logprob": -0.1
            },
            {
                "text": "How can we help you today?",
                "start": 2000,
                "end": 3500,
                "avg_logprob": -0.15
            }
        ],
        "words": [
            {"text": "Hello", "probability": 0.98, "start": 0, "end": 500},
            {"text": "this", "probability": 0.97, "start": 500, "end": 700},
            {"text": "is", "probability": 0.99, "start": 700, "end": 800},
            {"text": "Hunt", "probability": 0.96, "start": 800, "end": 1000},
            {"text": "&", "probability": 0.98, "start": 1000, "end": 1050},
            {"text": "Henriques", "probability": 0.95, "start": 1050, "end": 1500},
            {"text": "law", "probability": 0.97, "start": 1500, "end": 1700},
            {"text": "firm", "probability": 0.96, "start": 1700, "end": 1900}
        ]
    }


@pytest.fixture
def provider_results_fixture(sample_assemblyai_response, sample_openai_response) -> Dict[str, Any]:
    """Combined provider results structure for reconciliation testing."""
    return {
        "job_id": "test-job-001",
        "audio_file_url": "test://sample.mp3",
        "processing_status": "completed",
        "providers": {
            "assemblyai": {
                "status": "completed",
                "result": sample_assemblyai_response
            },
            "openai": {
                "status": "completed", 
                "result": sample_openai_response
            }
        }
    }


@pytest.fixture
def expected_name_correction() -> Dict[str, str]:
    """Expected name correction for Hunt & Henriques test case."""
    return {
        "input_assemblyai": "Hunt and Henriquez",
        "input_openai": "Hunt & Henriques", 
        "expected_output": "Hunt & Henriques",
        "reasoning": "OpenAI version has correct spelling and proper ampersand format"
    }