# Generated ADK agent module for creative_writer
# Source: examples/creative_writer

from google.adk.agents import Agent

# Tool definitions
# Tool: generate_character
def generate_character(genre: str = "fantasy", role: str = "protagonist") -> dict:
    """Generate a basic character profile."""
    import random
    
    names = {
        "fantasy": ["Aria", "Thorne", "Lyra", "Kael", "Zara", "Darius"],
        "modern": ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley"],
        "historical": ["Eleanor", "William", "Margaret", "Edward", "Catherine", "Thomas"]
    }
    
    traits = ["brave", "curious", "mysterious", "witty", "determined", "compassionate", "rebellious", "wise"]
    
    return {
        "name": random.choice(names.get(genre, names["modern"])),
        "role": role,
        "primary_trait": random.choice(traits),
        "secondary_trait": random.choice([t for t in traits if t != random.choice(traits)]),
        "genre": genre
    }

tool_0 = generate_character


# Agent: creative_writer
# Description: Creative writing assistant for stories, poems, and creative content
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='creative_writer',
    description='''Creative writing assistant for stories, poems, and creative content''',
    instruction='''You are a creative writing assistant named Aurora. You help with  in the  genre.

Your specialties include:
- Storytelling and narrative structure
- Character development
- Setting and world-building
- Dialogue and voice
- Poetry and creative expression
- Content ideation and brainstorming

Your writing style:
- Engaging and imaginative
- Vivid descriptions and imagery
- Emotional depth and resonance
- Original and unique perspectives
- Attention to pacing and flow

Guidelines:
- Be creative and original
- Ask about preferences and constraints
- Provide multiple options when appropriate
- Explain creative choices
- Encourage creativity in others''',
    tools=[tool_0]
)
