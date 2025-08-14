# Generated ADK agent module for sequential_review
# Source: examples/sequential_review

from google.adk.agents import Agent


# Agent: sequential_review
# Description: Sequential review workflow that processes content through multiple stages
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='sequential_review',
    description='''Sequential review workflow that processes content through multiple stages''',
    instruction='''You are a helpful AI assistant.'''
)
