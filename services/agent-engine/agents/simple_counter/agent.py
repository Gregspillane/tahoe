# Generated ADK agent module for simple-counter
# Source: custom/simple_counter

from google.adk.agents import Agent


# Agent: simple_counter
# Description: Dynamic custom agent that counts and processes items
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='simple_counter',
    description='''Dynamic custom agent that counts and processes items''',
    instruction='''You are a helpful AI assistant.'''
)
