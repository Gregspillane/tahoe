#!/usr/bin/env python3
"""
ADK Component Verification Script
Comprehensive verification of all Google ADK components
"""

import os
import sys
from typing import Dict, Any, List
import traceback


def verify_imports() -> bool:
    """Verify all ADK imports work correctly."""
    print("\n" + "="*60)
    print("ADK IMPORT VERIFICATION")
    print("="*60)
    
    success = True
    
    # Test agent imports
    try:
        from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
        print("✓ Agent imports successful")
        print("  - LlmAgent (also aliased as Agent)")
        print("  - SequentialAgent")
        print("  - ParallelAgent")
        print("  - LoopAgent")
        print("  - BaseAgent")
    except ImportError as e:
        print(f"✗ Agent imports failed: {e}")
        success = False
    
    # Test runner imports
    try:
        from google.adk.runners import InMemoryRunner
        print("✓ Runner imports successful")
        print("  - InMemoryRunner")
    except ImportError as e:
        print(f"✗ Runner imports failed: {e}")
        success = False
    
    # Test session imports
    try:
        from google.adk.sessions import InMemorySessionService
        print("✓ Session imports successful")
        print("  - InMemorySessionService")
    except ImportError as e:
        print(f"✗ Session imports failed: {e}")
        success = False
    
    # Test tool imports
    try:
        from google.adk.tools import FunctionTool, google_search
        print("✓ Tool imports successful")
        print("  - FunctionTool")
        print("  - google_search")
    except ImportError as e:
        print(f"✗ Tool imports failed: {e}")
        success = False
    
    # Test event imports
    try:
        from google.adk.events import Event
        print("✓ Event imports successful")
        print("  - Event")
    except ImportError as e:
        print(f"✗ Event imports failed: {e}")
        success = False
    
    return success


def test_agent_creation() -> bool:
    """Test creating different agent types."""
    print("\n" + "="*60)
    print("AGENT CREATION TESTS")
    print("="*60)
    
    success = True
    
    try:
        from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
        
        # Test LlmAgent
        print("\n1. Testing LlmAgent creation...")
        llm_agent = LlmAgent(
            name="test_llm",
            model="gemini-2.0-flash",
            instruction="You are a test agent for verification purposes",
            description="Test LLM agent"
        )
        print(f"✓ Created LlmAgent: {llm_agent.name}")
        print(f"  - Model: {llm_agent.model}")
        print(f"  - Has instruction: {bool(llm_agent.instruction)}")
        
        # Test Agent alias
        print("\n2. Testing Agent alias (should be same as LlmAgent)...")
        from google.adk.agents import Agent
        alias_agent = Agent(
            name="test_alias",
            model="gemini-2.0-flash",
            instruction="Testing Agent alias"
        )
        print(f"✓ Created Agent (alias): {alias_agent.name}")
        print(f"  - Type matches LlmAgent: {type(alias_agent).__name__ == 'LlmAgent'}")
        
        # Test SequentialAgent
        print("\n3. Testing SequentialAgent creation...")
        seq_agent = SequentialAgent(
            name="test_sequential",
            sub_agents=[llm_agent],
            description="Test sequential workflow"
        )
        print(f"✓ Created SequentialAgent: {seq_agent.name}")
        print(f"  - Sub-agents count: {len(seq_agent.sub_agents)}")
        
        # Test ParallelAgent
        print("\n4. Testing ParallelAgent creation...")
        # Create new agents for parallel (can't reuse agents with parents)
        par_agent1 = LlmAgent(
            name="par_agent1",
            model="gemini-2.0-flash",
            instruction="Parallel agent 1"
        )
        par_agent2 = LlmAgent(
            name="par_agent2",
            model="gemini-2.0-flash",
            instruction="Parallel agent 2"
        )
        par_agent = ParallelAgent(
            name="test_parallel",
            sub_agents=[par_agent1, par_agent2],
            description="Test parallel workflow"
        )
        print(f"✓ Created ParallelAgent: {par_agent.name}")
        print(f"  - Sub-agents count: {len(par_agent.sub_agents)}")
        
        # Test LoopAgent
        print("\n5. Testing LoopAgent creation...")
        # Create new agent for loop (can't reuse agent with parent)
        loop_sub = LlmAgent(
            name="loop_sub",
            model="gemini-2.0-flash",
            instruction="Loop sub-agent"
        )
        loop_agent = LoopAgent(
            name="test_loop",
            sub_agents=[loop_sub],  # LoopAgent takes sub_agents as a list
            max_iterations=3,
            description="Test loop workflow"
        )
        print(f"✓ Created LoopAgent: {loop_agent.name}")
        print(f"  - Sub-agents count: {len(loop_agent.sub_agents)}")
        print(f"  - Max iterations: {loop_agent.max_iterations}")
        
        # Test BaseAgent (for custom agents)
        print("\n6. Testing BaseAgent inheritance...")
        class CustomAgent(BaseAgent):
            def __init__(self, name: str):
                super().__init__(name=name, description="Custom agent")
        
        custom_agent = CustomAgent(name="test_custom")
        print(f"✓ Created CustomAgent (extends BaseAgent): {custom_agent.name}")
        
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        traceback.print_exc()
        success = False
    
    return success


def test_runner_execution() -> bool:
    """Test runner functionality."""
    print("\n" + "="*60)
    print("RUNNER EXECUTION TESTS")
    print("="*60)
    
    success = True
    
    try:
        from google.adk.agents import LlmAgent
        from google.adk.runners import InMemoryRunner
        
        # Create a simple agent
        print("\n1. Creating agent for runner test...")
        agent = LlmAgent(
            name="runner_test",
            model="gemini-2.0-flash",
            instruction="You are a test agent. Respond with 'Runner test successful'"
        )
        print(f"✓ Agent created: {agent.name}")
        
        # Create runner
        print("\n2. Creating InMemoryRunner...")
        runner = InMemoryRunner(agent, app_name="verify_app")
        print("✓ InMemoryRunner created")
        print(f"  - App name: verify_app")
        
        # Test session service
        print("\n3. Testing session service...")
        session_service = runner.session_service
        print("✓ Session service obtained")
        
        # Create session
        print("\n4. Creating session...")
        # Use sync version for simplicity
        try:
            # Try sync version first
            if hasattr(session_service, 'create_session_sync'):
                session = session_service.create_session_sync(
                    app_name="verify_app",
                    user_id="test-user"
                )
            else:
                # Fall back to async with immediate result
                import asyncio
                async def create():
                    return await session_service.create_session(
                        app_name="verify_app",
                        user_id="test-user"
                    )
                session = asyncio.run(create())
            
            print(f"✓ Session created")
            print(f"  - Session ID: {session.id}")
            print(f"  - User ID: {session.user_id}")
            print(f"  - App name: {session.app_name}")
        except Exception as e:
            print(f"✗ Session creation failed: {e}")
            success = False
        
        # Note: Actual execution would require API key
        print("\n5. Runner methods available:")
        print(f"  - run() method exists: {hasattr(runner, 'run')}")
        print(f"  - run_async() method exists: {hasattr(runner, 'run_async')}")
        
    except Exception as e:
        print(f"✗ Runner execution failed: {e}")
        traceback.print_exc()
        success = False
    
    return success


def test_tool_integration() -> bool:
    """Test tool wrapping and integration."""
    print("\n" + "="*60)
    print("TOOL INTEGRATION TESTS")
    print("="*60)
    
    success = True
    
    try:
        from google.adk.tools import FunctionTool
        from google.adk.agents import LlmAgent
        
        # Test automatic function wrapping
        print("\n1. Testing automatic function wrapping...")
        
        def simple_calculator(a: int, b: int, operation: str = "add") -> int:
            """Simple calculator function for testing."""
            if operation == "add":
                return a + b
            elif operation == "subtract":
                return a - b
            elif operation == "multiply":
                return a * b
            else:
                return 0
        
        # Functions can be passed directly to agents (automatic wrapping)
        agent_with_tool = LlmAgent(
            name="tool_test",
            model="gemini-2.0-flash",
            instruction="You are a calculator agent",
            tools=[simple_calculator]  # Automatic wrapping
        )
        print("✓ Agent created with automatically wrapped function")
        print(f"  - Tools count: {len(agent_with_tool.tools)}")
        
        # Test explicit FunctionTool wrapping
        print("\n2. Testing explicit FunctionTool wrapping...")
        explicit_tool = FunctionTool(simple_calculator)
        print("✓ FunctionTool created explicitly")
        
        # Test with explicitly wrapped tool
        agent_explicit = LlmAgent(
            name="explicit_tool_test",
            model="gemini-2.0-flash",
            instruction="You are a calculator agent",
            tools=[explicit_tool]
        )
        print("✓ Agent created with explicitly wrapped FunctionTool")
        
        # Test built-in tools
        print("\n3. Testing built-in tools...")
        from google.adk.tools import google_search
        
        agent_with_search = LlmAgent(
            name="search_test",
            model="gemini-2.0-flash",
            instruction="You are a search agent",
            tools=[google_search]
        )
        print("✓ Agent created with built-in google_search tool")
        
        # Test multiple tools
        print("\n4. Testing multiple tools...")
        
        def text_analyzer(text: str) -> dict:
            """Analyze text properties."""
            return {
                "length": len(text),
                "words": len(text.split()),
                "uppercase": text.isupper()
            }
        
        multi_tool_agent = LlmAgent(
            name="multi_tool_test",
            model="gemini-2.0-flash",
            instruction="You have multiple tools",
            tools=[simple_calculator, text_analyzer]  # Multiple tools
        )
        print("✓ Agent created with multiple tools")
        print(f"  - Tools count: {len(multi_tool_agent.tools)}")
        
    except Exception as e:
        print(f"✗ Tool integration failed: {e}")
        traceback.print_exc()
        success = False
    
    return success


def test_session_management() -> bool:
    """Test session management capabilities."""
    print("\n" + "="*60)
    print("SESSION MANAGEMENT TESTS")
    print("="*60)
    
    success = True
    
    try:
        from google.adk.agents import LlmAgent
        from google.adk.runners import InMemoryRunner
        from google.adk.sessions import InMemorySessionService
        
        # Create agent and runner
        print("\n1. Setting up agent and runner...")
        agent = LlmAgent(
            name="session_test",
            model="gemini-2.0-flash",
            instruction="Session management test agent"
        )
        runner = InMemoryRunner(agent, app_name="session_app")
        print("✓ Agent and runner created")
        
        # Get session service
        print("\n2. Testing session service...")
        session_service = runner.session_service
        print(f"✓ Session service type: {type(session_service).__name__}")
        
        # Create multiple sessions
        print("\n3. Testing multiple sessions...")
        # Use sync version or handle async properly
        try:
            if hasattr(session_service, 'create_session_sync'):
                session1 = session_service.create_session_sync(
                    app_name="session_app",
                    user_id="user1"
                )
                session2 = session_service.create_session_sync(
                    app_name="session_app",
                    user_id="user2"
                )
            else:
                import asyncio
                async def create_sessions():
                    s1 = await session_service.create_session(
                        app_name="session_app",
                        user_id="user1"
                    )
                    s2 = await session_service.create_session(
                        app_name="session_app",
                        user_id="user2"
                    )
                    return s1, s2
                session1, session2 = asyncio.run(create_sessions())
            
            print(f"✓ Created session 1: {session1.id}")
            print(f"✓ Created session 2: {session2.id}")
            print(f"  - Sessions are unique: {session1.id != session2.id}")
        except Exception as e:
            print(f"✗ Multiple sessions failed: {e}")
            success = False
        
        # Test session with initial state
        print("\n4. Testing session with initial state...")
        try:
            if hasattr(session_service, 'create_session_sync'):
                # create_session_sync doesn't support initial_state
                session_with_state = session_service.create_session_sync(
                    app_name="session_app",
                    user_id="user3"
                )
                print(f"✓ Created session (sync doesn't support initial_state): {session_with_state.id}")
            else:
                import asyncio
                async def create_with_state():
                    return await session_service.create_session(
                        app_name="session_app",
                        user_id="user3",
                        initial_state={"counter": 0, "messages": []}
                    )
                session_with_state = asyncio.run(create_with_state())
                print(f"✓ Created session with initial state: {session_with_state.id}")
        except Exception as e:
            print(f"✗ Session with state failed: {e}")
            success = False
        
        # Test session retrieval
        print("\n5. Testing session operations...")
        print(f"  - get_session method exists: {hasattr(session_service, 'get_session')}")
        print(f"  - list_sessions method exists: {hasattr(session_service, 'list_sessions')}")
        print(f"  - delete_session method exists: {hasattr(session_service, 'delete_session')}")
        
    except Exception as e:
        print(f"✗ Session management failed: {e}")
        traceback.print_exc()
        success = False
    
    return success


def verify_all_components() -> Dict[str, Any]:
    """Run all verification tests and return results."""
    print("\n" + "="*60)
    print("GOOGLE ADK COMPONENT VERIFICATION")
    print("="*60)
    
    results = {
        "imports": False,
        "agent_creation": False,
        "runner_execution": False,
        "tool_integration": False,
        "session_management": False,
        "overall": False
    }
    
    # Run all tests
    results["imports"] = verify_imports()
    results["agent_creation"] = test_agent_creation()
    results["runner_execution"] = test_runner_execution()
    results["tool_integration"] = test_tool_integration()
    results["session_management"] = test_session_management()
    
    # Calculate overall success
    results["overall"] = all([
        results["imports"],
        results["agent_creation"],
        results["runner_execution"],
        results["tool_integration"],
        results["session_management"]
    ])
    
    # Print summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    for key, value in results.items():
        if key != "overall":
            status = "✓ PASSED" if value else "✗ FAILED"
            print(f"{key.replace('_', ' ').title()}: {status}")
    
    print("\n" + "="*60)
    if results["overall"]:
        print("✓ ALL ADK COMPONENTS VERIFIED SUCCESSFULLY")
    else:
        print("✗ SOME COMPONENTS FAILED VERIFICATION")
    print("="*60)
    
    return results


if __name__ == "__main__":
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run verification
    results = verify_all_components()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall"] else 1)