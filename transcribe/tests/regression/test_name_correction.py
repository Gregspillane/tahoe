"""
Regression tests for name correction capabilities in the intelligent reconciliation pipeline.
This test validates the Hunt & Henriques correction scenario that was successfully implemented.
"""

import pytest
import asyncio
import os
from reconciliation.reconciler import TranscriptionReconciler


class TestNameCorrection:
    """Test suite for validating name correction capabilities."""
    
    @pytest.fixture
    def google_api_key(self):
        """Get Google API key from environment for testing."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set in environment")
        return api_key
    
    @pytest.fixture
    def reconciler(self, google_api_key):
        """Initialize TranscriptionReconciler for testing."""
        return TranscriptionReconciler(
            gemini_api_key=google_api_key,
            gemini_model="gemini-2.5-pro",
            max_tokens=4096,
            temperature=0.1
        )
    
    @pytest.fixture
    def hunt_henriques_test_case(self):
        """The standard Hunt & Henriques name correction test case."""
        return {
            "assemblyai_result": {
                "provider": "assemblyai",
                "job_id": "test-name-correction",
                "text": "Hello, this is Hunt and Henriquez law firm. How can we help you today?",
                "confidence": 0.95,
                "words": [
                    {"text": "Hello", "confidence": 0.98, "start": 0, "end": 500},
                    {"text": "this", "confidence": 0.97, "start": 500, "end": 700},
                    {"text": "is", "confidence": 0.99, "start": 700, "end": 800},
                    {"text": "Hunt", "confidence": 0.95, "start": 800, "end": 1000},
                    {"text": "and", "confidence": 0.98, "start": 1000, "end": 1100},
                    {"text": "Henriquez", "confidence": 0.85, "start": 1100, "end": 1500},  # Misspelled
                    {"text": "law", "confidence": 0.97, "start": 1500, "end": 1700},
                    {"text": "firm", "confidence": 0.96, "start": 1700, "end": 1900}
                ]
            },
            "openai_result": {
                "provider": "openai", 
                "job_id": "test-name-correction",
                "text": "Hello, this is Hunt & Henriques law firm. How can we help you today?",
                "confidence": 0.92,
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
                ]
            },
            "expected_output": "Hunt & Henriques",  # Correct spelling with ampersand
            "expected_discrepancies": ["Proper noun spelling", "Conjunction difference"]
        }
    
    @pytest.mark.asyncio
    async def test_hunt_henriques_name_correction(self, reconciler, hunt_henriques_test_case):
        """Test that Hunt & Henriques name correction works consistently."""
        
        # Create provider results structure
        provider_results = {
            "job_id": "test-name-correction",
            "audio_file_url": "test://name-correction.mp3",
            "processing_status": "completed",
            "providers": {
                "assemblyai": {
                    "status": "completed",
                    "result": hunt_henriques_test_case["assemblyai_result"]
                },
                "openai": {
                    "status": "completed", 
                    "result": hunt_henriques_test_case["openai_result"]
                }
            }
        }
        
        # Perform reconciliation
        result = await reconciler.reconcile_provider_results("test-name-correction", provider_results)
        
        # Validate reconciliation completed successfully
        assert result["reconciliation_status"] == "completed", "Reconciliation should complete successfully"
        
        # Validate name correction occurred
        final_transcript = result["final_transcript"]
        assert "Henriques" in final_transcript, "Final transcript should contain correctly spelled 'Henriques'"
        assert "Henriquez" not in final_transcript, "Final transcript should not contain misspelled 'Henriquez'"
        
        # Validate proper firm name format (Hunt & Henriques or Hunt and Henriques is acceptable)
        assert ("Hunt & Henriques" in final_transcript or "Hunt and Henriques" in final_transcript), \
               "Final transcript should contain proper firm name format"
        
        # Validate high confidence (should be > 0.8 for successful reconciliation)
        assert result["confidence_score"] > 0.8, f"Confidence score {result['confidence_score']} should be > 0.8"
        
        # Validate audit trail exists
        assert "audit_trail" in result, "Result should contain audit trail"
        audit_trail = result["audit_trail"]
        assert "decisions" in audit_trail, "Audit trail should contain decisions"
        
        # Validate discrepancies were detected
        decisions = audit_trail["decisions"]
        assert len(decisions) > 0, "Should have at least one reconciliation decision"
        
        # Check that discrepancies were identified
        found_discrepancies = []
        for decision in decisions:
            found_discrepancies.extend(decision.get("discrepancies_found", []))
        
        assert len(found_discrepancies) > 0, "Should detect discrepancies between providers"
    
    @pytest.mark.asyncio 
    async def test_name_correction_prefers_higher_accuracy(self, reconciler, hunt_henriques_test_case):
        """Test that reconciliation chooses the more accurate provider for name correction."""
        
        provider_results = {
            "job_id": "test-accuracy-preference",
            "audio_file_url": "test://accuracy-test.mp3", 
            "processing_status": "completed",
            "providers": {
                "assemblyai": {
                    "status": "completed",
                    "result": hunt_henriques_test_case["assemblyai_result"]
                },
                "openai": {
                    "status": "completed",
                    "result": hunt_henriques_test_case["openai_result"]
                }
            }
        }
        
        result = await reconciler.reconcile_provider_results("test-accuracy-preference", provider_results)
        
        # Get the decision details
        audit_trail = result["audit_trail"]
        decisions = audit_trail["decisions"]
        
        # For name correction, should prefer the provider with correct spelling
        # In our test case, OpenAI has "Henriques" (correct) vs AssemblyAI "Henriquez" (incorrect)
        final_transcript = result["final_transcript"]
        
        # The reconciliation should choose the correct spelling
        if "Henriques" in final_transcript:
            # OpenAI version was chosen - verify reasoning mentions accuracy/spelling
            decision_reasoning = []
            for decision in decisions:
                decision_reasoning.append(decision.get("reasoning", "").lower())
            
            reasoning_text = " ".join(decision_reasoning)
            assert ("spelling" in reasoning_text or "accurate" in reasoning_text or "correct" in reasoning_text), \
                   "Reasoning should mention spelling or accuracy for name correction"
    
    @pytest.mark.asyncio
    async def test_single_provider_fallback_preserves_names(self, reconciler, hunt_henriques_test_case):
        """Test that single provider fallback still preserves available names correctly."""
        
        # Test with only AssemblyAI succeeding
        provider_results_assemblyai_only = {
            "job_id": "test-single-provider",
            "audio_file_url": "test://single-provider.mp3",
            "processing_status": "completed", 
            "providers": {
                "assemblyai": {
                    "status": "completed",
                    "result": hunt_henriques_test_case["assemblyai_result"]
                },
                "openai": {
                    "status": "failed",
                    "error": "API timeout"
                }
            }
        }
        
        result = await reconciler.reconcile_provider_results("test-single-provider", provider_results_assemblyai_only)
        
        assert result["reconciliation_status"] == "single_provider_only", "Should use single provider fallback"
        assert "Hunt" in result["final_transcript"], "Should preserve firm name even in single provider mode"
        assert result["provider_used"] == "assemblyai", "Should indicate which provider was used"
    
    def test_name_correction_test_data_validity(self, hunt_henriques_test_case):
        """Validate that our test data represents the name correction scenario properly."""
        
        assemblyai_text = hunt_henriques_test_case["assemblyai_result"]["text"]
        openai_text = hunt_henriques_test_case["openai_result"]["text"]
        
        # Verify the test case represents the actual scenario
        assert "Henriquez" in assemblyai_text, "AssemblyAI test data should contain misspelled 'Henriquez'"
        assert "Henriques" in openai_text, "OpenAI test data should contain correctly spelled 'Henriques'"
        assert "Hunt and" in assemblyai_text, "AssemblyAI should use 'and' conjunction"  
        assert "Hunt &" in openai_text, "OpenAI should use '&' conjunction"
        
        # Verify expected output is realistic
        expected = hunt_henriques_test_case["expected_output"]
        assert expected == "Hunt & Henriques", "Expected output should be the correct firm name format"


if __name__ == "__main__":
    # Allow running this test directly
    pytest.main([__file__, "-v"])