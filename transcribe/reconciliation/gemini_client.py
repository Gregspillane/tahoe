"""
Google Gemini API client for intelligent transcription reconciliation.
Uses Gemini 2.5 Pro's advanced reasoning capabilities to resolve discrepancies
between AssemblyAI and Google Speech transcription results.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)


@dataclass
class ReconciliationDecision:
    """Represents a reconciliation decision for a segment."""
    segment_index: int
    chosen_text: str
    chosen_provider: str  # "assemblyai", "google_speech", or "reconciled"
    confidence_score: float
    reasoning: str
    discrepancies_found: List[str]
    original_assemblyai: str
    original_google: str


@dataclass
class ReconciliationResult:
    """Complete reconciliation result for a transcription job."""
    job_id: str
    final_transcript: str
    decisions: List[ReconciliationDecision]
    overall_confidence: float
    processing_time_seconds: float
    model_used: str
    metadata: Dict[str, Any]


class GeminiReconciliationError(Exception):
    """Custom exception for Gemini reconciliation errors."""
    pass


class GeminiClient:
    """Google Gemini API client for transcription reconciliation."""
    
    def __init__(
        self, 
        api_key: str,
        model: str = "gemini-2.5-pro",
        max_tokens: int = 8192,
        temperature: float = 0.1
    ):
        """
        Initialize Gemini client for reconciliation.
        
        Args:
            api_key: Google API key for Gemini API
            model: Gemini model to use (default: gemini-2.5-pro)
            max_tokens: Maximum tokens for response
            temperature: Low temperature for consistent reconciliation decisions
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        try:
            self.gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.8,
                    top_k=10
                ),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            logger.info(f"Initialized Gemini client with model: {model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise GeminiReconciliationError(f"Failed to initialize Gemini: {str(e)}")
    
    async def reconcile_transcripts(
        self, 
        job_id: str,
        assemblyai_result: Dict,
        google_result: Dict
    ) -> ReconciliationResult:
        """
        Reconcile transcripts from AssemblyAI and Google Speech using Gemini reasoning.
        
        Args:
            job_id: Unique job identifier
            assemblyai_result: Complete AssemblyAI transcription result
            google_result: Complete Google Speech transcription result
            
        Returns:
            ReconciliationResult with final transcript and decision audit trail
        """
        start_time = datetime.now()
        logger.info(f"Starting Gemini reconciliation for job {job_id}")
        
        try:
            # Extract and normalize transcript segments
            assemblyai_segments = self._extract_segments(assemblyai_result, "assemblyai")
            google_segments = self._extract_segments(google_result, "google_speech")
            
            # Align segments for comparison
            aligned_segments = self._align_segments(assemblyai_segments, google_segments)
            
            # Perform reconciliation using Gemini
            decisions = await self._reconcile_with_gemini(job_id, aligned_segments)
            
            # Assemble final transcript
            final_transcript = self._assemble_final_transcript(decisions)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(decisions)
            
            # Create result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ReconciliationResult(
                job_id=job_id,
                final_transcript=final_transcript,
                decisions=decisions,
                overall_confidence=overall_confidence,
                processing_time_seconds=processing_time,
                model_used=self.model,
                metadata={
                    "assemblyai_segments": len(assemblyai_segments),
                    "google_segments": len(google_segments),
                    "aligned_segments": len(aligned_segments),
                    "discrepancies_found": sum(1 for d in decisions if d.discrepancies_found),
                    "reconciliation_timestamp": start_time.isoformat()
                }
            )
            
            logger.info(f"Gemini reconciliation completed for job {job_id} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Gemini reconciliation failed for job {job_id}: {e}")
            raise GeminiReconciliationError(f"Reconciliation failed: {str(e)}")
    
    def _extract_segments(self, provider_result: Dict, provider_name: str) -> List[Dict]:
        """Extract normalized segments from provider result."""
        segments = []
        
        try:
            if provider_name == "assemblyai":
                # AssemblyAI format
                if "utterances" in provider_result:
                    for i, utterance in enumerate(provider_result["utterances"]):
                        segments.append({
                            "index": i,
                            "text": utterance.get("text", ""),
                            "confidence": utterance.get("confidence", 0.0),
                            "start": utterance.get("start", 0),
                            "end": utterance.get("end", 0),
                            "speaker": utterance.get("speaker", "Unknown"),
                            "provider": provider_name
                        })
                elif "text" in provider_result:
                    # Fallback to full text
                    segments.append({
                        "index": 0,
                        "text": provider_result["text"],
                        "confidence": provider_result.get("confidence", 0.0),
                        "start": 0,
                        "end": 0,
                        "speaker": "Unknown",
                        "provider": provider_name
                    })
                    
            elif provider_name == "google_speech":
                # Google Speech format
                if "results" in provider_result:
                    for i, result in enumerate(provider_result["results"]):
                        if "alternatives" in result and result["alternatives"]:
                            alternative = result["alternatives"][0]
                            segments.append({
                                "index": i,
                                "text": alternative.get("transcript", ""),
                                "confidence": alternative.get("confidence", 0.0),
                                "start": 0,  # Google doesn't always provide timestamps
                                "end": 0,
                                "speaker": f"Speaker {i % 2}",  # Simple speaker assignment
                                "provider": provider_name
                            })
                elif "transcript" in provider_result:
                    # Fallback to full transcript
                    segments.append({
                        "index": 0,
                        "text": provider_result["transcript"],
                        "confidence": provider_result.get("confidence", 0.0),
                        "start": 0,
                        "end": 0,
                        "speaker": "Unknown",
                        "provider": provider_name
                    })
            
            logger.debug(f"Extracted {len(segments)} segments from {provider_name}")
            return segments
            
        except Exception as e:
            logger.error(f"Failed to extract segments from {provider_name}: {e}")
            return []
    
    def _align_segments(self, assemblyai_segments: List[Dict], google_segments: List[Dict]) -> List[Dict]:
        """Align segments from both providers for comparison."""
        aligned = []
        
        # Simple alignment strategy: pair by index or create comparison pairs
        max_segments = max(len(assemblyai_segments), len(google_segments))
        
        for i in range(max_segments):
            assemblyai_segment = assemblyai_segments[i] if i < len(assemblyai_segments) else None
            google_segment = google_segments[i] if i < len(google_segments) else None
            
            aligned.append({
                "index": i,
                "assemblyai": assemblyai_segment,
                "google_speech": google_segment
            })
        
        logger.debug(f"Aligned {len(aligned)} segment pairs for comparison")
        return aligned
    
    async def _reconcile_with_gemini(self, job_id: str, aligned_segments: List[Dict]) -> List[ReconciliationDecision]:
        """Use Gemini to reconcile aligned segments."""
        decisions = []
        
        for segment_pair in aligned_segments:
            try:
                decision = await self._reconcile_segment_pair(job_id, segment_pair)
                decisions.append(decision)
            except Exception as e:
                logger.error(f"Failed to reconcile segment {segment_pair['index']} for job {job_id}: {e}")
                # Create fallback decision
                assemblyai_text = segment_pair.get("assemblyai", {}).get("text", "") if segment_pair.get("assemblyai") else ""
                google_text = segment_pair.get("google_speech", {}).get("text", "") if segment_pair.get("google_speech") else ""
                
                decisions.append(ReconciliationDecision(
                    segment_index=segment_pair["index"],
                    chosen_text=assemblyai_text or google_text,
                    chosen_provider="assemblyai" if assemblyai_text else "google_speech",
                    confidence_score=0.5,
                    reasoning="Fallback due to reconciliation error",
                    discrepancies_found=["reconciliation_error"],
                    original_assemblyai=assemblyai_text,
                    original_google=google_text
                ))
        
        return decisions
    
    async def _reconcile_segment_pair(self, job_id: str, segment_pair: Dict) -> ReconciliationDecision:
        """Reconcile a single segment pair using Gemini reasoning."""
        assemblyai_segment = segment_pair.get("assemblyai")
        google_segment = segment_pair.get("google_speech")
        
        assemblyai_text = assemblyai_segment.get("text", "") if assemblyai_segment else ""
        google_text = google_segment.get("text", "") if google_segment else ""
        assemblyai_confidence = assemblyai_segment.get("confidence", 0.0) if assemblyai_segment else 0.0
        google_confidence = google_segment.get("confidence", 0.0) if google_segment else 0.0
        
        # If texts are identical, no reconciliation needed
        if assemblyai_text.strip().lower() == google_text.strip().lower():
            return ReconciliationDecision(
                segment_index=segment_pair["index"],
                chosen_text=assemblyai_text,
                chosen_provider="both_agree",
                confidence_score=max(assemblyai_confidence, google_confidence),
                reasoning="Both providers produced identical text",
                discrepancies_found=[],
                original_assemblyai=assemblyai_text,
                original_google=google_text
            )
        
        # Build reconciliation prompt
        prompt = self._build_reconciliation_prompt(
            assemblyai_text, google_text,
            assemblyai_confidence, google_confidence,
            segment_pair["index"]
        )
        
        try:
            # Get Gemini's reasoning and decision
            response = await asyncio.to_thread(self.gemini_model.generate_content, prompt)
            
            if not response.text:
                raise GeminiReconciliationError("Empty response from Gemini")
            
            # Parse the structured response
            decision = self._parse_gemini_response(
                response.text, 
                segment_pair["index"],
                assemblyai_text,
                google_text
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Gemini API call failed for segment {segment_pair['index']}: {e}")
            raise GeminiReconciliationError(f"Gemini reconciliation failed: {str(e)}")
    
    def _build_reconciliation_prompt(
        self, 
        assemblyai_text: str, 
        google_text: str,
        assemblyai_confidence: float,
        google_confidence: float,
        segment_index: int
    ) -> str:
        """Build a structured prompt for Gemini reconciliation."""
        
        return f"""You are an expert transcription reconciliation system. Your task is to analyze two transcripts from different speech-to-text providers and determine the most accurate version.

**Segment {segment_index} Analysis:**

**AssemblyAI Result:**
Text: "{assemblyai_text}"
Confidence: {assemblyai_confidence:.3f}

**Google Speech Result:**
Text: "{google_text}"
Confidence: {google_confidence:.3f}

**Your Task:**
1. Compare both transcripts carefully for accuracy, grammar, and context
2. Identify specific discrepancies (word differences, punctuation, capitalization, etc.)
3. Determine which version is more accurate, or create an improved version
4. Consider confidence scores but prioritize content accuracy
5. Provide reasoning for your decision

**Response Format (JSON):**
```json
{{
    "chosen_text": "final chosen or reconciled text",
    "chosen_provider": "assemblyai|google_speech|reconciled",
    "confidence_score": 0.95,
    "reasoning": "detailed explanation of why this choice was made",
    "discrepancies_found": ["specific difference 1", "specific difference 2"],
    "improvements_made": "description of any improvements if reconciled version was created"
}}
```

**Guidelines:**
- Preserve speaker intent and meaning
- Maintain natural speech patterns and contractions
- Fix obvious errors (grammar, spelling, punctuation)
- Choose the more contextually appropriate version
- If both are poor quality, create a reconciled version
- Be specific about discrepancies found

Provide only the JSON response, no other text."""

    def _parse_gemini_response(
        self, 
        response_text: str, 
        segment_index: int,
        original_assemblyai: str,
        original_google: str
    ) -> ReconciliationDecision:
        """Parse Gemini's structured JSON response into a ReconciliationDecision."""
        
        try:
            # Extract JSON from response (handle cases where Gemini adds extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            parsed = json.loads(json_text)
            
            return ReconciliationDecision(
                segment_index=segment_index,
                chosen_text=parsed.get("chosen_text", original_assemblyai),
                chosen_provider=parsed.get("chosen_provider", "assemblyai"),
                confidence_score=float(parsed.get("confidence_score", 0.5)),
                reasoning=parsed.get("reasoning", "No reasoning provided"),
                discrepancies_found=parsed.get("discrepancies_found", []),
                original_assemblyai=original_assemblyai,
                original_google=original_google
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse Gemini response for segment {segment_index}: {e}")
            logger.error(f"Raw response: {response_text}")
            
            # Return fallback decision
            return ReconciliationDecision(
                segment_index=segment_index,
                chosen_text=original_assemblyai or original_google,
                chosen_provider="assemblyai" if original_assemblyai else "google_speech",
                confidence_score=0.5,
                reasoning="Failed to parse Gemini response, using fallback",
                discrepancies_found=["parse_error"],
                original_assemblyai=original_assemblyai,
                original_google=original_google
            )
    
    def _assemble_final_transcript(self, decisions: List[ReconciliationDecision]) -> str:
        """Assemble the final transcript from reconciliation decisions."""
        segments = []
        
        for decision in decisions:
            if decision.chosen_text.strip():
                segments.append(decision.chosen_text.strip())
        
        # Join with appropriate spacing
        final_transcript = " ".join(segments)
        
        # Clean up spacing and punctuation
        final_transcript = self._clean_transcript(final_transcript)
        
        return final_transcript
    
    def _clean_transcript(self, transcript: str) -> str:
        """Clean and format the final transcript."""
        import re
        
        # Fix multiple spaces
        transcript = re.sub(r'\s+', ' ', transcript)
        
        # Fix spacing around punctuation
        transcript = re.sub(r'\s+([.!?])', r'\1', transcript)
        transcript = re.sub(r'([.!?])\s*', r'\1 ', transcript)
        
        # Fix spacing around commas
        transcript = re.sub(r'\s*,\s*', ', ', transcript)
        
        # Capitalize after sentence endings
        transcript = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), transcript)
        
        # Capitalize first letter
        if transcript:
            transcript = transcript[0].upper() + transcript[1:]
        
        return transcript.strip()
    
    def _calculate_overall_confidence(self, decisions: List[ReconciliationDecision]) -> float:
        """Calculate overall confidence score from all decisions."""
        if not decisions:
            return 0.0
        
        total_confidence = sum(decision.confidence_score for decision in decisions)
        return total_confidence / len(decisions)