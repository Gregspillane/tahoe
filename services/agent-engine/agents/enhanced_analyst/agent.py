# Generated ADK agent module for enhanced_analyst
# Source: examples/enhanced_analyst

from google.adk.agents import Agent

# Tool definitions
from google.adk.tools import google_search
tool_0 = google_search

# Tool: analyze_sentiment
def analyze_sentiment(text: str) -> dict:
    """Simple sentiment analysis tool"""
    positive_words = ['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful']
    negative_words = ['bad', 'terrible', 'awful', 'negative', 'horrible', 'poor']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        sentiment = "positive"
        confidence = min(0.9, 0.5 + (pos_count - neg_count) * 0.1)
    elif neg_count > pos_count:
        sentiment = "negative" 
        confidence = min(0.9, 0.5 + (neg_count - pos_count) * 0.1)
    else:
        sentiment = "neutral"
        confidence = 0.5
    
    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_indicators": pos_count,
        "negative_indicators": neg_count
    }

tool_1 = analyze_sentiment

# Tool: word_counter
def word_counter(text: str) -> dict:
    """Count words, characters, and basic statistics"""
    import re
    
    # Clean and split text
    words = re.findall(r'\b\w+\b', text.lower())
    sentences = re.split(r'[.!?]+', text)
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "character_count_no_spaces": len(text.replace(' ', '')),
        "sentence_count": len([s for s in sentences if s.strip()]),
        "average_words_per_sentence": round(len(words) / max(1, len([s for s in sentences if s.strip()])), 2),
        "unique_words": len(set(words))
    }

tool_2 = word_counter


# Agent: enhanced_analyst
# Description: Enhanced analyst agent demonstrating LLM builder features with multiple tool types and fallback models
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='enhanced_analyst',
    description='''Enhanced analyst agent demonstrating LLM builder features with multiple tool types and fallback models''',
    instruction='''You are a $assistant with expertise in $general.
Your primary task is to $help users.

Guidelines:
- Analyze data thoroughly before drawing conclusions
- Use available tools to gather additional information when needed
- Provide evidence-based recommendations
- Cite sources when using external research

Context: You are working on $''',
    tools=[tool_0, tool_1, tool_2]
)
