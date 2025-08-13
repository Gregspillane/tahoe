from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()
load_dotenv(f"config/{os.getenv('ENVIRONMENT', 'development')}.env")

app = FastAPI(
    title="Agent Engine",
    description="Universal agent orchestration platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agent-engine"}

@app.get("/adk/verify")
async def verify_adk() -> Dict[str, Any]:
    """Verify ADK components are working correctly."""
    results = {
        "status": "verifying",
        "components": {}
    }
    
    # Test imports
    try:
        from google.adk.agents import LlmAgent, Agent, SequentialAgent, ParallelAgent, LoopAgent, BaseAgent
        results["components"]["imports"] = "success"
        results["components"]["agent_types"] = ["LlmAgent", "SequentialAgent", "ParallelAgent", "LoopAgent", "BaseAgent"]
    except Exception as e:
        results["components"]["imports"] = f"failed: {str(e)}"
    
    # Test agent creation
    try:
        from google.adk.agents import LlmAgent
        agent = LlmAgent(
            name="verify",
            model="gemini-2.0-flash",
            instruction="Verification agent for testing ADK components"
        )
        results["components"]["agent_creation"] = "success"
        results["components"]["test_agent"] = {
            "name": agent.name,
            "model": agent.model
        }
    except Exception as e:
        results["components"]["agent_creation"] = f"failed: {str(e)}"
    
    # Test runner
    try:
        from google.adk.runners import InMemoryRunner
        from google.adk.agents import LlmAgent
        
        if 'agent' not in locals():
            agent = LlmAgent(name="verify", model="gemini-2.0-flash", instruction="Test")
        
        runner = InMemoryRunner(agent, app_name="verify")
        results["components"]["runner"] = "success"
        results["components"]["runner_methods"] = {
            "has_run": hasattr(runner, 'run'),
            "has_run_async": hasattr(runner, 'run_async'),
            "has_session_service": hasattr(runner, 'session_service')
        }
    except Exception as e:
        results["components"]["runner"] = f"failed: {str(e)}"
    
    # Test session
    try:
        if 'runner' in locals():
            session_service = runner.session_service()
            session = session_service.create_session(
                app_name="verify",
                user_id="test-user"
            )
            results["components"]["session"] = "success"
            results["components"]["session_info"] = {
                "session_id": str(session.id),
                "user_id": session.user_id,
                "app_name": session.app_name
            }
        else:
            results["components"]["session"] = "skipped: runner not available"
    except Exception as e:
        results["components"]["session"] = f"failed: {str(e)}"
    
    # Test tools
    try:
        from google.adk.tools import FunctionTool, google_search
        
        def test_tool(x: int) -> int:
            return x * 2
        
        wrapped_tool = FunctionTool(test_tool)
        results["components"]["tools"] = "success"
        results["components"]["tool_features"] = {
            "function_tool": "available",
            "google_search": "available",
            "automatic_wrapping": "supported"
        }
    except Exception as e:
        results["components"]["tools"] = f"failed: {str(e)}"
    
    # Overall status
    all_success = all(
        v == "success" 
        for k, v in results["components"].items() 
        if isinstance(v, str) and k in ["imports", "agent_creation", "runner", "session", "tools"]
    )
    
    results["status"] = "verified" if all_success else "partial"
    results["all_components_operational"] = all_success
    
    return results