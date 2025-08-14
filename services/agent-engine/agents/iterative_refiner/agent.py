# Generated ADK agent module for iterative_refiner
# Source: examples/iterative_refiner

from google.adk.agents import Agent


# Agent: iterative_refiner
# Description: Loop workflow that iteratively refines content until quality threshold is met
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='iterative_refiner',
    description='''Loop workflow that iteratively refines content until quality threshold is met''',
    instruction='''You are a helpful AI assistant.'''
)
