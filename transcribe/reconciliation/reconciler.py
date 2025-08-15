"""
Main reconciliation service that orchestrates transcription reconciliation
using Google Gemini 2.5 Pro's advanced reasoning capabilities.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from .gemini_client import GeminiClient, GeminiReconciliationError, ReconciliationResult

logger = logging.getLogger(__name__)


class TranscriptionReconciler:
    """
    Main reconciliation service that coordinates discrepancy detection
    and resolution using Google Gemini 2.5 Pro.
    """
    
    def __init__(
        self,
        gemini_api_key: str,
        gemini_model: str = "gemini-2.5-pro",
        max_tokens: int = 8192,
        temperature: float = 0.1
    ):
        """
        Initialize the reconciliation service.
        
        Args:
            gemini_api_key: Google API key for Gemini API
            gemini_model: Gemini model to use for reconciliation
            max_tokens: Maximum tokens for Gemini responses
            temperature: Temperature for Gemini (low for consistency)
        """
        self.gemini_client = GeminiClient(
            api_key=gemini_api_key,
            model=gemini_model,
            max_tokens=max_tokens,
            temperature=temperature
        )
        logger.info(f"TranscriptionReconciler initialized with {gemini_model}")
    
    async def reconcile_provider_results(
        self,
        job_id: str,
        provider_results: Dict
    ) -> Dict:
        """
        Reconcile transcription results from multiple providers.
        
        Args:
            job_id: Unique identifier for the transcription job
            provider_results: Results from multiple transcription providers
            
        Returns:
            Dictionary containing reconciled transcript and detailed analysis
        """
        start_time = datetime.now()
        logger.info(f"Starting reconciliation for job {job_id}")
        
        try:
            # Extract provider results
            assemblyai_result = self._extract_provider_result(provider_results, "assemblyai")
            google_result = self._extract_provider_result(provider_results, "google_speech")
            
            # Validate we have results from both providers
            if not assemblyai_result and not google_result:
                raise ValueError("No valid transcription results found from any provider")
            
            # Handle single provider success
            if not assemblyai_result:
                logger.warning(f"AssemblyAI failed for job {job_id}, using Google Speech only")
                return self._create_single_provider_result(job_id, google_result, "google_speech")
            
            if not google_result:
                logger.warning(f"Google Speech failed for job {job_id}, using AssemblyAI only")
                return self._create_single_provider_result(job_id, assemblyai_result, "assemblyai")
            
            # Perform Gemini-based reconciliation
            reconciliation_result = await self.gemini_client.reconcile_transcripts(
                job_id=job_id,
                assemblyai_result=assemblyai_result,
                google_result=google_result
            )
            
            # Create final result structure
            result = self._create_reconciliation_result(
                job_id=job_id,
                reconciliation_result=reconciliation_result,
                provider_results=provider_results,
                start_time=start_time
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Reconciliation completed for job {job_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Reconciliation failed for job {job_id}: {e}")
            return self._create_error_result(job_id, str(e), provider_results)
    
    def _extract_provider_result(self, provider_results: Dict, provider_name: str) -> Optional[Dict]:
        """Extract and validate result from a specific provider."""
        try:
            provider_data = provider_results.get("providers", {}).get(provider_name)
            
            if not provider_data:
                logger.warning(f"No data found for provider {provider_name}")
                return None
            
            if provider_data.get("status") != "completed":
                logger.warning(f"Provider {provider_name} did not complete successfully: {provider_data.get('status')}")
                return None
            
            result = provider_data.get("result")
            if not result:
                logger.warning(f"No result data found for provider {provider_name}")
                return None
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract result for provider {provider_name}: {e}")
            return None
    
    def _create_single_provider_result(self, job_id: str, provider_result: Dict, provider_name: str) -> Dict:
        """Create result structure when only one provider succeeded."""
        
        # Extract text from provider result
        if provider_name == "assemblyai":
            transcript_text = provider_result.get("text", "")
        elif provider_name == "google_speech":
            # Google Speech may have different structure
            if "results" in provider_result and provider_result["results"]:
                transcript_text = " ".join([
                    result["alternatives"][0]["transcript"] 
                    for result in provider_result["results"] 
                    if result.get("alternatives")
                ])
            else:
                transcript_text = provider_result.get("transcript", "")
        else:
            transcript_text = str(provider_result)
        
        return {
            "job_id": job_id,
            "reconciliation_status": "single_provider_only",
            "final_transcript": transcript_text,
            "provider_used": provider_name,
            "confidence_score": provider_result.get("confidence", 0.0),
            "reconciliation_metadata": {
                "method": "single_provider_fallback",
                "reason": f"Only {provider_name} provided valid results",
                "timestamp": datetime.now().isoformat()
            },
            "audit_trail": {
                "decisions": [],
                "discrepancies_found": 0,
                "segments_reconciled": 0
            }
        }
    
    def _create_reconciliation_result(
        self,
        job_id: str,
        reconciliation_result: ReconciliationResult,
        provider_results: Dict,
        start_time: datetime
    ) -> Dict:
        """Create final result structure from Gemini reconciliation."""
        
        # Count discrepancies and reconciliation stats
        total_discrepancies = sum(len(decision.discrepancies_found) for decision in reconciliation_result.decisions)
        reconciled_segments = sum(1 for decision in reconciliation_result.decisions if decision.chosen_provider == "reconciled")
        
        return {
            "job_id": job_id,
            "reconciliation_status": "completed",
            "final_transcript": reconciliation_result.final_transcript,
            "confidence_score": reconciliation_result.overall_confidence,
            "processing_time_seconds": reconciliation_result.processing_time_seconds,
            
            "reconciliation_metadata": {
                "model_used": reconciliation_result.model_used,
                "method": "gemini_intelligent_reconciliation",
                "timestamp": start_time.isoformat(),
                "segments_processed": len(reconciliation_result.decisions),
                "discrepancies_found": total_discrepancies,
                "segments_reconciled": reconciled_segments,
                "segments_from_assemblyai": sum(1 for d in reconciliation_result.decisions if d.chosen_provider == "assemblyai"),
                "segments_from_google": sum(1 for d in reconciliation_result.decisions if d.chosen_provider == "google_speech"),
                "segments_agreed": sum(1 for d in reconciliation_result.decisions if d.chosen_provider == "both_agree")
            },
            
            "audit_trail": {
                "decisions": [
                    {
                        "segment_index": decision.segment_index,
                        "chosen_text": decision.chosen_text,
                        "chosen_provider": decision.chosen_provider,
                        "confidence_score": decision.confidence_score,
                        "reasoning": decision.reasoning,
                        "discrepancies_found": decision.discrepancies_found,
                        "original_assemblyai": decision.original_assemblyai,
                        "original_google": decision.original_google
                    }
                    for decision in reconciliation_result.decisions
                ],
                "summary": {
                    "total_segments": len(reconciliation_result.decisions),
                    "total_discrepancies": total_discrepancies,
                    "reconciliation_rate": reconciled_segments / len(reconciliation_result.decisions) if reconciliation_result.decisions else 0,
                    "average_confidence": reconciliation_result.overall_confidence
                }
            },
            
            "provider_results": provider_results  # Preserve original results for audit
        }
    
    def _create_error_result(self, job_id: str, error_message: str, provider_results: Dict) -> Dict:
        """Create error result when reconciliation fails."""
        
        # Try to extract any available text as fallback
        fallback_text = ""
        fallback_provider = "unknown"
        
        try:
            providers = provider_results.get("providers", {})
            for provider_name, provider_data in providers.items():
                if provider_data.get("status") == "completed" and provider_data.get("result"):
                    result = provider_data["result"]
                    if provider_name == "assemblyai" and "text" in result:
                        fallback_text = result["text"]
                        fallback_provider = provider_name
                        break
                    elif provider_name == "google_speech":
                        if "results" in result and result["results"]:
                            fallback_text = " ".join([
                                res["alternatives"][0]["transcript"] 
                                for res in result["results"] 
                                if res.get("alternatives")
                            ])
                            fallback_provider = provider_name
                            break
        except Exception as e:
            logger.error(f"Failed to extract fallback text: {e}")
        
        return {
            "job_id": job_id,
            "reconciliation_status": "failed",
            "final_transcript": fallback_text,
            "error_message": error_message,
            "fallback_provider": fallback_provider,
            "confidence_score": 0.0,
            
            "reconciliation_metadata": {
                "method": "error_fallback",
                "timestamp": datetime.now().isoformat(),
                "error": error_message
            },
            
            "audit_trail": {
                "decisions": [],
                "error": error_message,
                "fallback_used": bool(fallback_text)
            },
            
            "provider_results": provider_results
        }
    
    async def get_reconciliation_summary(self, reconciliation_result: Dict) -> Dict:
        """
        Generate a high-level summary of reconciliation results.
        
        Args:
            reconciliation_result: Result from reconcile_provider_results
            
        Returns:
            Summary dictionary with key metrics and insights
        """
        try:
            audit_trail = reconciliation_result.get("audit_trail", {})
            metadata = reconciliation_result.get("reconciliation_metadata", {})
            
            summary = {
                "job_id": reconciliation_result.get("job_id"),
                "status": reconciliation_result.get("reconciliation_status"),
                "final_transcript_length": len(reconciliation_result.get("final_transcript", "")),
                "overall_confidence": reconciliation_result.get("confidence_score", 0.0),
                "processing_time": reconciliation_result.get("processing_time_seconds", 0.0),
                
                "quality_metrics": {
                    "segments_processed": metadata.get("segments_processed", 0),
                    "discrepancies_found": metadata.get("discrepancies_found", 0),
                    "reconciliation_rate": audit_trail.get("summary", {}).get("reconciliation_rate", 0.0),
                    "provider_agreement_rate": metadata.get("segments_agreed", 0) / max(metadata.get("segments_processed", 1), 1)
                },
                
                "provider_contribution": {
                    "assemblyai_segments": metadata.get("segments_from_assemblyai", 0),
                    "google_segments": metadata.get("segments_from_google", 0),
                    "reconciled_segments": metadata.get("segments_reconciled", 0),
                    "agreed_segments": metadata.get("segments_agreed", 0)
                },
                
                "recommendations": self._generate_recommendations(reconciliation_result)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate reconciliation summary: {e}")
            return {
                "error": f"Failed to generate summary: {str(e)}",
                "job_id": reconciliation_result.get("job_id"),
                "status": "summary_error"
            }
    
    def _generate_recommendations(self, reconciliation_result: Dict) -> list:
        """Generate recommendations based on reconciliation analysis."""
        recommendations = []
        
        try:
            metadata = reconciliation_result.get("reconciliation_metadata", {})
            confidence = reconciliation_result.get("confidence_score", 0.0)
            
            # Confidence-based recommendations
            if confidence < 0.7:
                recommendations.append("Low overall confidence - consider manual review")
            elif confidence > 0.95:
                recommendations.append("High confidence result - likely very accurate")
            
            # Discrepancy-based recommendations
            discrepancies = metadata.get("discrepancies_found", 0)
            segments = metadata.get("segments_processed", 1)
            
            if discrepancies / segments > 0.3:
                recommendations.append("High discrepancy rate - audio quality may be poor")
            elif discrepancies / segments < 0.1:
                recommendations.append("Low discrepancy rate - providers mostly agreed")
            
            # Provider performance recommendations
            assemblyai_segments = metadata.get("segments_from_assemblyai", 0)
            google_segments = metadata.get("segments_from_google", 0)
            
            if assemblyai_segments > google_segments * 2:
                recommendations.append("AssemblyAI performed significantly better")
            elif google_segments > assemblyai_segments * 2:
                recommendations.append("Google Speech performed significantly better")
            else:
                recommendations.append("Both providers contributed roughly equally")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]