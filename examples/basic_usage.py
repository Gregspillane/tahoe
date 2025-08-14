"""
Basic usage example for Tahoe API
"""

import httpx
import asyncio
import json
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:9000"
SERVICE_TOKEN = "development_token_change_in_production"


async def create_agent(name: str, agent_type: str, config: Dict[str, Any]):
    """Create a new agent"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/agents",
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
            json={
                "name": name,
                "type": agent_type,
                "config": config,
                "description": "Example agent"
            }
        )
        response.raise_for_status()
        return response.json()


async def execute_agent(agent_id: str, input_text: str, session_id: str = None):
    """Execute an agent"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/agents/{agent_id}/execute",
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
            json={
                "agent_id": agent_id,
                "input": input_text,
                "session_id": session_id,
                "context": {}
            }
        )
        response.raise_for_status()
        return response.json()


async def main():
    """Main example flow"""
    
    # 1. Create a simple assistant agent
    print("Creating simple assistant agent...")
    agent_config = {
        "model": "gemini-2.5-flash-lite",
        "instruction": "You are a helpful assistant. Answer questions clearly and concisely."
    }
    
    agent_result = await create_agent(
        name="my_assistant",
        agent_type="llm",
        config=agent_config
    )
    print(f"Agent created: {agent_result}")
    
    # 2. Execute the agent
    print("\nExecuting agent...")
    exec_result = await execute_agent(
        agent_id="my_assistant",
        input_text="What is the capital of France?"
    )
    print(f"Response: {exec_result['response']}")
    
    # 3. Continue conversation with session
    print("\nContinuing conversation...")
    session_id = exec_result['session_id']
    exec_result2 = await execute_agent(
        agent_id="my_assistant",
        input_text="What is its population?",
        session_id=session_id
    )
    print(f"Response: {exec_result2['response']}")
    
    # 4. Create a workflow agent
    print("\nCreating research workflow...")
    workflow_config = {
        "sub_agents": [
            {
                "name": "researcher",
                "type": "llm",
                "config": {
                    "model": "gemini-2.5-flash-lite",
                    "instruction": "Research the topic and provide detailed information.",
                    "output_key": "research"
                }
            },
            {
                "name": "summarizer",
                "type": "llm",
                "config": {
                    "model": "gemini-2.5-flash-lite",
                    "instruction": "Summarize the research from {research} into key points."
                }
            }
        ]
    }
    
    workflow_result = await create_agent(
        name="research_workflow",
        agent_type="sequential",
        config=workflow_config
    )
    print(f"Workflow created: {workflow_result}")
    
    # 5. Execute the workflow
    print("\nExecuting workflow...")
    workflow_exec = await execute_agent(
        agent_id="research_workflow",
        input_text="Tell me about renewable energy"
    )
    print(f"Workflow result: {workflow_exec['response']}")


if __name__ == "__main__":
    asyncio.run(main())