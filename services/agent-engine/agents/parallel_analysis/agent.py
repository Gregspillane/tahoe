# Generated ADK agent module for parallel_analysis
# Source: examples/parallel_analysis

from google.adk.agents import Agent


# Agent: parallel_analysis
# Description: Parallel analysis workflow that runs multiple analyzers concurrently
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='parallel_analysis',
    description='''Parallel analysis workflow that runs multiple analyzers concurrently''',
    instruction='''You are a helpful AI assistant.'''
)
