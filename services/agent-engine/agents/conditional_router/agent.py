# Generated ADK agent module for conditional-router
# Source: custom/conditional_router

from google.adk.agents import Agent


# Agent: conditional_router
# Description: Custom agent that routes to different sub-agents based on input conditions
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='conditional_router',
    description='''Custom agent that routes to different sub-agents based on input conditions''',
    instruction='''You are a helpful AI assistant.'''
)
