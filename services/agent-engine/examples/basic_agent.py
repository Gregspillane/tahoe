#!/usr/bin/env python3
"""
Basic Agent Creation Examples
Demonstrates fundamental ADK agent patterns
"""

import os
import sys
from typing import Optional
from google.adk.agents import LlmAgent, Agent
from google.adk.runners import InMemoryRunner


def create_basic_agent() -> LlmAgent:
    """Create a basic LLM agent with minimal configuration."""
    print("\n" + "="*60)
    print("CREATING BASIC AGENT")
    print("="*60)
    
    # Create a simple agent
    agent = LlmAgent(
        name="basic_assistant",
        model="gemini-2.0-flash",
        instruction="""You are a helpful assistant. 
        Provide clear, concise answers to questions.
        Be friendly and professional.""",
        description="A basic helpful assistant"
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Model: {agent.model}")
    print(f"  - Description: {agent.description}")
    
    return agent


def create_agent_with_parameters() -> LlmAgent:
    """Create an agent with additional parameters."""
    print("\n" + "="*60)
    print("CREATING PARAMETERIZED AGENT")
    print("="*60)
    
    # Agent with custom parameters
    # Note: Model parameters like temperature are set at runtime, not in agent creation
    agent = LlmAgent(
        name="precise_assistant",
        model="gemini-2.0-flash",
        instruction="""You are a precise technical assistant.
        Focus on accuracy and detail in your responses.
        Use technical terminology when appropriate.""",
        description="Precise technical assistant"
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Model: {agent.model}")
    print(f"  - Note: Model parameters set at runtime via model config")
    
    return agent


def create_agent_with_tools() -> LlmAgent:
    """Create an agent with tool capabilities."""
    print("\n" + "="*60)
    print("CREATING AGENT WITH TOOLS")
    print("="*60)
    
    # Define some simple tools
    def word_counter(text: str) -> dict:
        """Count words and characters in text."""
        words = text.split()
        return {
            "word_count": len(words),
            "char_count": len(text),
            "char_count_no_spaces": len(text.replace(" ", ""))
        }
    
    def text_formatter(text: str, style: str = "upper") -> str:
        """Format text in different styles."""
        if style == "upper":
            return text.upper()
        elif style == "lower":
            return text.lower()
        elif style == "title":
            return text.title()
        else:
            return text
    
    def simple_calculator(a: float, b: float, operation: str = "add") -> float:
        """Perform basic arithmetic operations."""
        operations = {
            "add": a + b,
            "subtract": a - b,
            "multiply": a * b,
            "divide": a / b if b != 0 else 0
        }
        return operations.get(operation, 0)
    
    # Create agent with tools
    agent = LlmAgent(
        name="tool_equipped_assistant",
        model="gemini-2.0-flash",
        instruction="""You are an assistant with access to several tools:
        1. word_counter - Count words and characters in text
        2. text_formatter - Format text in different styles
        3. simple_calculator - Perform arithmetic operations
        
        Use these tools when appropriate to help users.""",
        description="Assistant with text and math tools",
        tools=[word_counter, text_formatter, simple_calculator]  # Automatic wrapping
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - Model: {agent.model}")
    print(f"  - Tools available: {len(agent.tools)}")
    print("    • word_counter")
    print("    • text_formatter")
    print("    • simple_calculator")
    
    return agent


def create_specialized_agents():
    """Create multiple specialized agents for different tasks."""
    print("\n" + "="*60)
    print("CREATING SPECIALIZED AGENTS")
    print("="*60)
    
    # Code reviewer agent
    code_reviewer = LlmAgent(
        name="code_reviewer",
        model="gemini-2.0-flash",
        instruction="""You are a code review specialist.
        Review code for:
        - Correctness and logic errors
        - Code style and best practices
        - Performance considerations
        - Security vulnerabilities
        - Documentation quality
        
        Provide constructive feedback with specific suggestions.""",
        description="Specialized code review agent"
    )
    
    print(f"✓ Created agent: {code_reviewer.name}")
    print(f"  - Specialization: Code review")
    
    # Data analyst agent
    data_analyst = LlmAgent(
        name="data_analyst",
        model="gemini-2.0-flash",
        instruction="""You are a data analysis expert.
        Help users with:
        - Data interpretation
        - Statistical analysis
        - Trend identification
        - Visualization recommendations
        - Insights and patterns
        
        Explain findings in clear, non-technical language when needed.""",
        description="Data analysis specialist"
    )
    
    print(f"✓ Created agent: {data_analyst.name}")
    print(f"  - Specialization: Data analysis")
    
    # Creative writer agent
    creative_writer = LlmAgent(
        name="creative_writer",
        model="gemini-2.0-flash",
        instruction="""You are a creative writing assistant.
        Help users with:
        - Story development
        - Character creation
        - Dialogue writing
        - Descriptive passages
        - Plot development
        
        Be creative and imaginative in your suggestions.""",
        description="Creative writing assistant"
    )
    
    print(f"✓ Created agent: {creative_writer.name}")
    print(f"  - Specialization: Creative writing")
    
    return code_reviewer, data_analyst, creative_writer


def execute_agent(agent: Optional[LlmAgent] = None):
    """Demonstrate agent execution setup (without API key)."""
    print("\n" + "="*60)
    print("AGENT EXECUTION SETUP")
    print("="*60)
    
    if agent is None:
        agent = create_basic_agent()
    
    # Create runner for the agent
    runner = InMemoryRunner(agent, app_name="example_app")
    print(f"✓ Created InMemoryRunner for: {agent.name}")
    print(f"  - App name: example-app")
    
    # Create session
    session_service = runner.session_service
    # Use sync version if available
    if hasattr(session_service, 'create_session_sync'):
        session = session_service.create_session_sync(
            app_name="example_app",
            user_id="example-user"
        )
    else:
        # Fall back to async
        import asyncio
        async def create():
            return await session_service.create_session(
                app_name="example_app",
                user_id="example-user"
            )
        session = asyncio.run(create())
    
    print(f"✓ Created session")
    print(f"  - Session ID: {session.id}")
    print(f"  - User ID: {session.user_id}")
    
    # Note about execution
    print("\n📝 Note: Actual execution requires GEMINI_API_KEY to be set")
    print("   To execute, you would use:")
    print("   - runner.run(user_id, session_id, prompt) for synchronous")
    print("   - runner.run_async(user_id, session_id, prompt) for streaming")
    
    return runner, session


def demonstrate_agent_alias():
    """Demonstrate that Agent is an alias for LlmAgent."""
    print("\n" + "="*60)
    print("AGENT ALIAS DEMONSTRATION")
    print("="*60)
    
    # Create using LlmAgent
    llm_agent = LlmAgent(
        name="using_llmagent",
        model="gemini-2.0-flash",
        instruction="Created with LlmAgent"
    )
    
    # Create using Agent alias
    alias_agent = Agent(
        name="using_agent_alias",
        model="gemini-2.0-flash",
        instruction="Created with Agent alias"
    )
    
    print(f"✓ Created with LlmAgent: {llm_agent.name}")
    print(f"  - Type: {type(llm_agent).__name__}")
    
    print(f"✓ Created with Agent alias: {alias_agent.name}")
    print(f"  - Type: {type(alias_agent).__name__}")
    
    print(f"\n✓ Both are the same type: {type(llm_agent).__name__ == type(alias_agent).__name__}")


def main():
    """Run all basic agent examples."""
    print("\n" + "="*60)
    print("BASIC AGENT EXAMPLES")
    print("="*60)
    
    try:
        # Example 1: Basic agent
        basic = create_basic_agent()
        
        # Example 2: Parameterized agent
        parameterized = create_agent_with_parameters()
        
        # Example 3: Agent with tools
        with_tools = create_agent_with_tools()
        
        # Example 4: Specialized agents
        code_reviewer, data_analyst, creative_writer = create_specialized_agents()
        
        # Example 5: Execution setup
        runner, session = execute_agent(basic)
        
        # Example 6: Agent alias
        demonstrate_agent_alias()
        
        print("\n" + "="*60)
        print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error in examples: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run examples
    success = main()
    sys.exit(0 if success else 1)