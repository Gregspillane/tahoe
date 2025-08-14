# Generated ADK agent module for research_assistant
# Source: examples/research_assistant

from google.adk.agents import Agent

# Tool definitions
# Tool: evaluate_source
def evaluate_source(source_type: str, publication_year: int = None, peer_reviewed: bool = False) -> dict:
    """Evaluate source credibility and reliability."""
    
    credibility_scores = {
        "academic_journal": 9,
        "book": 8,
        "government_report": 8,
        "news_article": 6,
        "blog": 4,
        "social_media": 2,
        "unknown": 3
    }
    
    base_score = credibility_scores.get(source_type, 3)
    
    # Adjust for peer review
    if peer_reviewed and source_type in ["academic_journal", "book"]:
        base_score = min(10, base_score + 1)
    
    # Adjust for recency (if year provided)
    if publication_year:
        current_year = 2025
        age = current_year - publication_year
        if age > 10:
            base_score = max(1, base_score - 2)
        elif age > 5:
            base_score = max(1, base_score - 1)
    
    return {
        "credibility_score": base_score,
        "source_type": source_type,
        "peer_reviewed": peer_reviewed,
        "reliability": "high" if base_score >= 8 else "medium" if base_score >= 6 else "low",
        "notes": f"Score: {base_score}/10 based on source type and other factors"
    }

tool_0 = evaluate_source


# Agent: research_assistant
# Description: Research and analysis assistant for information gathering and synthesis
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='research_assistant',
    description='''Research and analysis assistant for information gathering and synthesis''',
    instruction='''You are Dr. Research, an expert research assistant specializing in general research.
You help with information gathering, analysis, and synthesis.

Your capabilities:
- Comprehensive literature review
- Data analysis and interpretation
- Fact-checking and verification
- Source evaluation and citation
- Research methodology guidance
- Information synthesis and summarization

Research principles:
- Accuracy and reliability first
- Multiple source verification
- Transparent about limitations
- Structured and organized output
- Critical thinking and analysis
- Proper attribution and citations

Guidelines:
- Always cite sources when possible
- Distinguish between facts and opinions
- Highlight conflicting information
- Suggest additional research directions
- Structure information logically
- Be thorough but concise''',
    tools=[tool_0]
)
