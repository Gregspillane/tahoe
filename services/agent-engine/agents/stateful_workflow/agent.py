# Generated ADK agent module for stateful-workflow
# Source: custom/stateful_workflow

from google.adk.agents import Agent


# Agent: stateful_workflow
# Description: Custom agent that maintains state across executions and supports workflow restart
root_agent = Agent(
    model='gemini-2.5-flash-lite',
    name='stateful_workflow',
    description='''Custom agent that maintains state across executions and supports workflow restart''',
    instruction='''You are a helpful AI assistant.'''
)
