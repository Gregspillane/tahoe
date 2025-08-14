# Generated ADK agent module for adaptive-orchestrator
# Source: custom/adaptive_orchestrator

from google.adk.agents import Agent


# Agent: adaptive_orchestrator
# Description: Custom agent that adaptively orchestrates sub-agents based on state
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='adaptive_orchestrator',
    description='''Custom agent that adaptively orchestrates sub-agents based on state''',
    instruction='''You are a helpful AI assistant.'''
)
