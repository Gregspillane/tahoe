from google.adk.agents import SequentialAgent, LlmAgent

# Agent 1: Extract metadata from transcript
metadata_agent = LlmAgent(
    name="metadata_extractor",
    model="gemini-2.0-flash-lite",
    instruction="""Extract the following metadata from the call transcript and format as JSON:
    - agent_name: The name of the agent/representative (if mentioned)
    - customer_name: The customer's name (if mentioned, use "Unknown" if not found)
    - call_date: Any date/time mentioned in the call (use "Not specified" if not found)
    - call_duration: Approximate length if discernible (use "Unknown" if not found)
    - main_topic: Brief description of the primary purpose of the call
    - account_type: Type of account being discussed (credit card, loan, etc., use "Unknown" if unclear)
    
    Return only valid JSON format.""",
    output_key="metadata"
)

# Agent 2: Check compliance using the existing compliance function
def check_fdcpa_compliance(transcript: str) -> dict:
    """
    Basic FDCPA compliance check for call transcripts.
    
    Args:
        transcript: The call transcript to analyze for FDCPA violations
        
    Returns:
        Dictionary containing compliance check results including violations and status
    """
    violations = []
    
    # Simple keyword-based checks for common FDCPA violations
    forbidden_phrases = [
        "arrest", "jail", "prison", "lawsuit", "wage garnishment",
        "sheriff", "court", "sue you", "legal action"
    ]
    
    transcript_lower = transcript.lower()
    
    for phrase in forbidden_phrases:
        if phrase in transcript_lower:
            violations.append(f"Potential FDCPA violation: mention of '{phrase}' without proper disclosure")
    
    # Check for proper identification
    if "this is an attempt to collect a debt" not in transcript_lower:
        violations.append("Missing required FDCPA disclosure: 'This is an attempt to collect a debt'")
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "total_violations": len(violations),
        "checked_items": ["FDCPA basic keywords", "Required disclosures"]
    }

compliance_agent = LlmAgent(
    name="compliance_checker",
    model="gemini-2.0-flash-lite",
    instruction="Use the compliance checking tool to analyze the transcript for FDCPA violations: {transcript}",
    tools=[check_fdcpa_compliance],
    output_key="compliance_results"
)

# Agent 3: Generate comprehensive scorecard
scorecard_agent = LlmAgent(
    name="scorecard_generator",
    model="gemini-2.0-flash-lite",
    instruction="""Based on the extracted metadata and compliance results, generate a comprehensive QA scorecard.

    Metadata: {metadata}
    Compliance Results: {compliance_results}
    
    Generate a detailed scorecard that includes:
    
    1. Overall Score (0-100): Calculate based on compliance status and call quality
    2. Compliance Score: Specific score for regulatory compliance (0-100)
    3. Key Findings: 3-5 bullet points of main observations
    4. Violations Summary: List any compliance violations found
    5. Recommendations: 2-3 specific actionable recommendations for improvement
    6. Call Quality Assessment: Brief assessment of professional conduct and communication
    7. Risk Level: LOW/MEDIUM/HIGH based on violations and overall conduct
    
    Format as a structured JSON response with clear sections.""",
    output_key="scorecard"
)

# Main workflow agent that coordinates all sub-agents
root_agent = SequentialAgent(
    name="qa_workflow",
    description="Complete QA analysis workflow that extracts metadata, checks compliance, and generates a comprehensive scorecard",
    sub_agents=[
        metadata_agent,
        compliance_agent,
        scorecard_agent
    ]
)