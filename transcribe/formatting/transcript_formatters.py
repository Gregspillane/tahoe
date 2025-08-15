"""
Transcript formatting classes for Phase 5 production storage.

Creates three optimized output formats:
1. Raw JSON - Complete reconciliation output with all metadata
2. Agent-optimized JSON - Cleaned structure for LLM consumption
3. Database text - Plain text for fast web display
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FormattedOutputs:
    """Container for all three output formats."""
    raw_json: Dict
    agent_optimized_json: Dict
    display_text: str
    word_count: int
    duration_seconds: Optional[int] = None


class TranscriptFormatter:
    """
    Main formatter that creates all three output formats from reconciliation results.
    """
    
    def __init__(self):
        """Initialize the transcript formatter."""
        self.logger = logger
    
    def format_reconciliation_result(
        self,
        job_id: str,
        tenant_id: str,
        reconciliation_result: Dict,
        original_filename: str = None
    ) -> FormattedOutputs:
        """
        Create all three output formats from reconciliation result.
        
        Args:
            job_id: UUID identifier for the job
            tenant_id: Tenant identifier for multi-tenant isolation
            reconciliation_result: Output from TranscriptionReconciler
            original_filename: Original audio filename if available
            
        Returns:
            FormattedOutputs containing all three formats
        """
        try:
            self.logger.info(f"Formatting transcription outputs for job {job_id}")
            
            # Extract basic information
            final_transcript = reconciliation_result.get("final_transcript", "")
            word_count = len(final_transcript.split()) if final_transcript else 0
            
            # Create raw JSON format (complete reconciliation output)
            raw_json = self._create_raw_json_format(
                job_id=job_id,
                tenant_id=tenant_id,
                reconciliation_result=reconciliation_result,
                original_filename=original_filename
            )
            
            # Create agent-optimized JSON format
            agent_optimized_json = self._create_agent_optimized_format(
                job_id=job_id,
                tenant_id=tenant_id,
                reconciliation_result=reconciliation_result,
                original_filename=original_filename
            )
            
            # Create display text format
            display_text = self._create_display_text_format(reconciliation_result)
            
            # Extract duration if available
            duration_seconds = self._extract_duration(reconciliation_result)
            
            self.logger.info(f"Successfully formatted outputs for job {job_id}: {word_count} words, {len(display_text)} chars")
            
            return FormattedOutputs(
                raw_json=raw_json,
                agent_optimized_json=agent_optimized_json,
                display_text=display_text,
                word_count=word_count,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.logger.error(f"Failed to format outputs for job {job_id}: {e}")
            raise ValueError(f"Transcript formatting failed: {str(e)}")
    
    def _create_raw_json_format(
        self,
        job_id: str,
        tenant_id: str,
        reconciliation_result: Dict,
        original_filename: str = None
    ) -> Dict:
        """
        Create raw JSON format with complete reconciliation details.
        
        This format preserves all reconciliation metadata, audit trails,
        and provider-specific information for debugging and compliance.
        """
        
        raw_format = {
            "format_version": "1.0",
            "format_type": "raw_reconciliation",
            "generated_at": datetime.now().isoformat(),
            
            # Job identification
            "job_metadata": {
                "job_id": job_id,
                "tenant_id": tenant_id,
                "original_filename": original_filename,
                "processing_status": reconciliation_result.get("reconciliation_status", "unknown")
            },
            
            # Complete reconciliation result
            "reconciliation": reconciliation_result,
            
            # Processing metadata
            "processing_metadata": {
                "formatter_version": "1.0",
                "processing_timestamp": datetime.now().isoformat(),
                "word_count": len(reconciliation_result.get("final_transcript", "").split()),
                "confidence_score": reconciliation_result.get("confidence_score", 0.0),
                "processing_time_seconds": reconciliation_result.get("processing_time_seconds", 0.0)
            }
        }
        
        return raw_format
    
    def _create_agent_optimized_format(
        self,
        job_id: str,
        tenant_id: str,
        reconciliation_result: Dict,
        original_filename: str = None
    ) -> Dict:
        """
        Create agent-optimized JSON format for LLM consumption.
        
        This format is cleaned and structured to minimize token usage
        while preserving essential information for analysis.
        """
        
        # Extract essential information
        final_transcript = reconciliation_result.get("final_transcript", "")
        confidence_score = reconciliation_result.get("confidence_score", 0.0)
        reconciliation_metadata = reconciliation_result.get("reconciliation_metadata", {})
        
        # Extract speaker information if available
        speakers = self._extract_speaker_information(reconciliation_result)
        
        # Extract key segments for context
        segments = self._extract_key_segments(reconciliation_result)
        
        # Create reconciliation summary
        reconciliation_summary = self._create_reconciliation_summary(reconciliation_result)
        
        agent_format = {
            "format_version": "1.0",
            "format_type": "agent_optimized",
            "generated_at": datetime.now().isoformat(),
            
            # Essential identification
            "job_id": job_id,
            "tenant_id": tenant_id,
            "original_filename": original_filename,
            
            # Core transcript data
            "transcript": {
                "text": final_transcript,
                "confidence": confidence_score,
                "word_count": len(final_transcript.split()) if final_transcript else 0,
                "speakers": speakers,
                "segments": segments
            },
            
            # Processing summary
            "processing_summary": {
                "status": reconciliation_result.get("reconciliation_status", "unknown"),
                "method": reconciliation_metadata.get("method", "unknown"),
                "reconciliation_summary": reconciliation_summary,
                "quality_indicators": {
                    "confidence_score": confidence_score,
                    "discrepancies_resolved": reconciliation_metadata.get("discrepancies_found", 0),
                    "provider_agreement": self._calculate_agreement_rate(reconciliation_result)
                }
            },
            
            # Metadata for analysis
            "metadata": {
                "processing_timestamp": reconciliation_metadata.get("timestamp"),
                "duration_seconds": self._extract_duration(reconciliation_result),
                "providers_used": self._extract_providers_used(reconciliation_result)
            }
        }
        
        return agent_format
    
    def _create_display_text_format(self, reconciliation_result: Dict) -> str:
        """
        Create clean display text for web UI.
        
        This format is optimized for fast database storage and retrieval
        for web display purposes.
        """
        
        final_transcript = reconciliation_result.get("final_transcript", "")
        
        if not final_transcript:
            return "[No transcript available]"
        
        # Clean up the transcript for display
        # Remove extra whitespace and normalize line breaks
        cleaned_text = " ".join(final_transcript.split())
        
        # Add basic formatting for readability
        # This is a simple implementation - could be enhanced with speaker labels, etc.
        if len(cleaned_text) > 1000:
            # For long transcripts, add some paragraph breaks for readability
            paragraphs = []
            sentences = cleaned_text.split('. ')
            current_paragraph = []
            
            for sentence in sentences:
                current_paragraph.append(sentence)
                if len(' '.join(current_paragraph)) > 500:  # ~500 chars per paragraph
                    paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = []
            
            # Add remaining sentences
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph))
            
            return '\n\n'.join(paragraphs)
        
        return cleaned_text
    
    def _extract_speaker_information(self, reconciliation_result: Dict) -> List[Dict]:
        """Extract speaker information from reconciliation result."""
        speakers = []
        
        try:
            # Try to extract from provider results
            provider_results = reconciliation_result.get("provider_results", {})
            providers = provider_results.get("providers", {})
            
            # Check AssemblyAI for speaker information
            assemblyai_data = providers.get("assemblyai", {})
            if assemblyai_data.get("status") == "completed":
                result = assemblyai_data.get("result", {})
                if "utterances" in result:
                    for utterance in result["utterances"]:
                        speaker_info = {
                            "speaker": utterance.get("speaker", "Unknown"),
                            "confidence": utterance.get("confidence", 0.0)
                        }
                        if speaker_info not in speakers:
                            speakers.append(speaker_info)
            
            return speakers
            
        except Exception as e:
            self.logger.warning(f"Failed to extract speaker information: {e}")
            return []
    
    def _extract_key_segments(self, reconciliation_result: Dict) -> List[Dict]:
        """Extract key segments for agent consumption."""
        segments = []
        
        try:
            audit_trail = reconciliation_result.get("audit_trail", {})
            decisions = audit_trail.get("decisions", [])
            
            # Include segments with high confidence or interesting reconciliation decisions
            for decision in decisions[:10]:  # Limit to first 10 segments for token efficiency
                if decision.get("confidence_score", 0.0) > 0.8 or decision.get("discrepancies_found"):
                    segment = {
                        "index": decision.get("segment_index", 0),
                        "text": decision.get("chosen_text", ""),
                        "confidence": decision.get("confidence_score", 0.0),
                        "reconciliation_applied": bool(decision.get("discrepancies_found"))
                    }
                    segments.append(segment)
            
            return segments
            
        except Exception as e:
            self.logger.warning(f"Failed to extract key segments: {e}")
            return []
    
    def _create_reconciliation_summary(self, reconciliation_result: Dict) -> str:
        """Create a brief reconciliation summary for agents."""
        try:
            metadata = reconciliation_result.get("reconciliation_metadata", {})
            
            segments_processed = metadata.get("segments_processed", 0)
            discrepancies_found = metadata.get("discrepancies_found", 0)
            method = metadata.get("method", "unknown")
            
            if method == "single_provider_fallback":
                provider = reconciliation_result.get("provider_used", "unknown")
                return f"Single provider result from {provider} (other provider failed)"
            
            if discrepancies_found == 0:
                return f"Providers agreed on all {segments_processed} segments"
            
            reconciliation_rate = discrepancies_found / segments_processed if segments_processed > 0 else 0
            
            if reconciliation_rate < 0.1:
                return f"Minimal discrepancies ({discrepancies_found}/{segments_processed} segments) - high provider agreement"
            elif reconciliation_rate < 0.3:
                return f"Moderate discrepancies ({discrepancies_found}/{segments_processed} segments) - reconciliation applied"
            else:
                return f"Significant discrepancies ({discrepancies_found}/{segments_processed} segments) - extensive reconciliation required"
            
        except Exception as e:
            self.logger.warning(f"Failed to create reconciliation summary: {e}")
            return "Reconciliation summary unavailable"
    
    def _calculate_agreement_rate(self, reconciliation_result: Dict) -> float:
        """Calculate provider agreement rate."""
        try:
            metadata = reconciliation_result.get("reconciliation_metadata", {})
            segments_processed = metadata.get("segments_processed", 0)
            segments_agreed = metadata.get("segments_agreed", 0)
            
            if segments_processed == 0:
                return 0.0
            
            return segments_agreed / segments_processed
            
        except Exception:
            return 0.0
    
    def _extract_duration(self, reconciliation_result: Dict) -> Optional[int]:
        """Extract audio duration from reconciliation result."""
        try:
            # Try to extract from provider results
            provider_results = reconciliation_result.get("provider_results", {})
            providers = provider_results.get("providers", {})
            
            # Check AssemblyAI first
            assemblyai_data = providers.get("assemblyai", {})
            if assemblyai_data.get("status") == "completed":
                result = assemblyai_data.get("result", {})
                if "audio_duration" in result:
                    return int(result["audio_duration"])
            
            # Check OpenAI
            openai_data = providers.get("openai", {})
            if openai_data.get("status") == "completed":
                result = openai_data.get("result", {})
                # OpenAI may store duration differently
                if "duration" in result:
                    return int(result["duration"])
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Failed to extract duration: {e}")
            return None
    
    def _extract_providers_used(self, reconciliation_result: Dict) -> List[str]:
        """Extract list of providers that were used."""
        providers_used = []
        
        try:
            if reconciliation_result.get("reconciliation_status") == "single_provider_only":
                provider = reconciliation_result.get("provider_used")
                if provider:
                    providers_used.append(provider)
            else:
                # Check which providers completed successfully
                provider_results = reconciliation_result.get("provider_results", {})
                providers = provider_results.get("providers", {})
                
                for provider_name, provider_data in providers.items():
                    if provider_data.get("status") == "completed":
                        providers_used.append(provider_name)
            
            return providers_used
            
        except Exception as e:
            self.logger.warning(f"Failed to extract providers used: {e}")
            return []


def create_transcript_formatter() -> TranscriptFormatter:
    """Factory function to create a transcript formatter instance."""
    return TranscriptFormatter()