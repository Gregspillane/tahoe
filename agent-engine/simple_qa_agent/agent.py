from google.adk.agents import Agent

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

root_agent = Agent(
    name="simple_qa_agent",
    model="gemini-2.0-flash-lite",
    description="A QA assistant that analyzes call transcripts for compliance and quality assurance.",
    instruction="""You are a QA specialist analyzing call transcripts for compliance violations.
    When given a transcript, use the compliance checking tool to identify any FDCPA violations.
    Provide a clear summary of the findings and any recommendations for improvement.""",
    tools=[check_fdcpa_compliance]
)