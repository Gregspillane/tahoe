# Generated agents for Tahoe Dev UI
# Created from agent specifications via composition system

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'src'))

from google.adk.agents import LlmAgent
from core.composition import AgentCompositionService

# Initialize composition service
composition_service = AgentCompositionService()

# Agent specifications to load
agent_specs = ['chat_assistant', 'code_helper', 'creative_writer', 'simple_demo', 'research_assistant', 'content_analyzer']

# Create agents from specifications
agents = []
context = {'role': 'assistant', 'domain': 'general', 'objective': 'help users test agent capabilities'}

for spec_name in agent_specs:
    try:
        agent = composition_service.build_agent_from_spec(spec_name, context)
        if agent:
            agents.append(agent)
            print(f'Loaded agent: {agent.name}')
    except Exception as e:
        print(f'Failed to load agent {spec_name}: {e}')

print(f'Total agents loaded: {len(agents)}')