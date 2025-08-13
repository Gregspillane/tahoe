# Google ADK Patterns and Best Practices

## Overview
This document contains verified patterns and best practices for using Google's Agent Development Kit (ADK) in Project Tahoe.

**Documentation Source**: https://google.github.io/adk-docs/  
**Package**: `google-adk` (Python)  
**Verification Date**: 2025-08-13

## Core ADK Components

### Agent Types

#### LlmAgent (Primary Agent Type)
```python
from google.adk.agents import LlmAgent, Agent  # Agent is alias for LlmAgent

agent = LlmAgent(
    name="analyzer",
    model="gemini-2.0-flash",
    instruction="You are an expert analyst...",
    description="Analyzes complex data",
    tools=[tool1, tool2],  # Functions or FunctionTool instances
    sub_agents=[agent1, agent2],  # Other agents as sub-agents
    temperature=0.2,
    max_tokens=8192
)
```

#### SequentialAgent (Workflow Pattern)
```python
from google.adk.agents import SequentialAgent

sequential = SequentialAgent(
    name="sequential-workflow",
    sub_agents=[step1_agent, step2_agent, step3_agent],
    description="Executes agents in sequence"
)
```

#### ParallelAgent (Concurrent Execution)
```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    name="parallel-workflow",
    sub_agents=[analyzer_a, analyzer_b, analyzer_c],
    description="Executes agents in parallel"
)
```

#### LoopAgent (Iterative Pattern)
```python
from google.adk.agents import LoopAgent

loop = LoopAgent(
    name="iterative-processor",
    sub_agent=processing_agent,
    max_iterations=5,
    description="Iterates until condition met"
)
```

#### BaseAgent (Custom Agents)
```python
from google.adk.agents import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
    
    def execute(self, input_data: dict) -> dict:
        # Custom execution logic
        return {"result": "processed"}
```

### Runner Pattern

#### InMemoryRunner (Primary Execution)
```python
from google.adk.runners import InMemoryRunner

# Create runner with agent
runner = InMemoryRunner(agent, app_name="agent-engine")

# Get session service
session_service = runner.session_service()

# Create session
session = session_service.create_session(
    app_name="agent-engine",
    user_id="user123",
    session_id="optional-custom-id"
)

# Synchronous execution
result = runner.run(session.user_id, session.id, input_data)

# Asynchronous streaming execution
for event in runner.run_async(session.user_id, session.id, input_data):
    process_event(event)
```

### Session Management

#### InMemorySessionService (Default)
```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

# Create session
session = session_service.create_session(
    app_name="agent-engine",
    user_id="user123",
    initial_state={"context": "value"},
    session_id="custom-id"  # Optional
)

# Get session
session = session_service.get_session("session-id")

# Update session state
session_service.update_state("session-id", {"new": "state"})

# Get conversation history
history = session_service.get_history("session-id")
```

### Tool Patterns

#### Automatic Function Wrapping (Preferred)
```python
# Most functions work directly without wrapping
def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of text."""
    return {"sentiment": "positive", "confidence": 0.85}

# Pass directly to agent
agent = LlmAgent(
    name="analyzer",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[analyze_sentiment]  # Automatic wrapping
)
```

#### Explicit FunctionTool Wrapping (When Needed)
```python
from google.adk.tools import FunctionTool

# Use FunctionTool for explicit control
def complex_tool(data: dict, options: dict = None) -> dict:
    """Complex tool requiring explicit wrapping."""
    return {"result": "processed"}

wrapped_tool = FunctionTool(complex_tool)

agent = LlmAgent(
    name="processor",
    model="gemini-2.0-flash",
    instruction="...",
    tools=[wrapped_tool]
)
```

#### Built-in Tools
```python
from google.adk.tools import google_search

agent = LlmAgent(
    name="researcher",
    model="gemini-2.0-flash",
    instruction="Research and analyze topics",
    tools=[google_search]
)
```

## Best Practices

### 1. Agent Composition

**DO**: Use sub_agents for hierarchical composition
```python
specialist_a = LlmAgent(name="specialist-a", ...)
specialist_b = LlmAgent(name="specialist-b", ...)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-2.0-flash",
    instruction="Coordinate specialists",
    sub_agents=[specialist_a, specialist_b]
)
```

**DON'T**: Create custom orchestration logic
```python
# Wrong - Don't manually orchestrate
result_a = agent_a.execute(data)
result_b = agent_b.execute(result_a)
```

### 2. Tool Management

**DO**: Let ADK handle function wrapping automatically
```python
def my_tool(param: str) -> str:
    return param.upper()

agent = LlmAgent(tools=[my_tool])  # Automatic wrapping
```

**DON'T**: Wrap unnecessarily
```python
# Wrong - Unnecessary wrapping
wrapped = FunctionTool(my_tool)  # Not needed for simple functions
```

### 3. Session Handling

**DO**: Use ADK session services
```python
runner = InMemoryRunner(agent, app_name="app")
session_service = runner.session_service()
session = session_service.create_session(...)
```

**DON'T**: Implement custom session management
```python
# Wrong - Don't create custom session tracking
class CustomSessionManager:
    def __init__(self):
        self.sessions = {}
```

### 4. Error Handling

**DO**: Use ADK's built-in error recovery
```python
# ADK handles retries and recovery automatically
result = runner.run(user_id, session_id, input_data)
```

**DON'T**: Implement custom retry logic
```python
# Wrong - Don't implement custom retries
for attempt in range(3):
    try:
        result = agent.execute(data)
        break
    except Exception:
        continue
```

### 5. Model Configuration

**DO**: Configure models via environment and parameters
```python
import os
os.environ["GEMINI_API_KEY"] = "your-key"

agent = LlmAgent(
    name="agent",
    model="gemini-2.0-flash",
    temperature=0.2,
    max_tokens=8192
)
```

**DON'T**: Hardcode API keys or model settings
```python
# Wrong - Don't hardcode credentials
agent = LlmAgent(
    api_key="hardcoded-key",  # Wrong
    model="gemini-2.0-flash"
)
```

## Universal Patterns for Tahoe

### Dynamic Agent Creation Pattern
```python
class UniversalAgentFactory:
    def build_agent(self, spec: dict, context: dict = None) -> BaseAgent:
        """Build any agent type from specification."""
        agent_type = spec["agent"]["type"]
        
        builders = {
            "llm": self._build_llm_agent,
            "sequential": self._build_sequential_agent,
            "parallel": self._build_parallel_agent,
            "loop": self._build_loop_agent,
            "custom": self._build_custom_agent
        }
        
        builder = builders.get(agent_type)
        if not builder:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return builder(spec, context)
```

### Tool Registry Pattern
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, name: str, function: callable):
        """Register tool for dynamic loading."""
        # Validate function signature
        self._validate_function(function)
        
        # Store for later use
        self.tools[name] = function
    
    def get_tools_for_agent(self, tool_names: list) -> list:
        """Get tools for agent creation."""
        return [self.tools[name] for name in tool_names if name in self.tools]
```

### Workflow Execution Pattern
```python
async def execute_workflow(template: dict, input_data: dict) -> dict:
    """Execute workflow from template."""
    # Build workflow agent
    workflow_agent = build_workflow_agent(template)
    
    # Create runner
    runner = InMemoryRunner(workflow_agent, app_name="workflow")
    
    # Create session
    session_service = runner.session_service()
    session = session_service.create_session(
        app_name="workflow",
        user_id="system"
    )
    
    # Execute with streaming
    results = []
    for event in runner.run_async(session.user_id, session.id, input_data):
        results.append(event)
    
    return process_results(results)
```

### Session Backend Selection Pattern
```python
def create_session_service(backend: str):
    """Create session service based on backend type."""
    if backend == "memory":
        from google.adk.sessions import InMemorySessionService
        return InMemorySessionService()
    elif backend == "redis":
        # Custom Redis implementation
        return RedisSessionService()
    elif backend == "vertex":
        # Vertex AI implementation
        return VertexSessionService()
    else:
        raise ValueError(f"Unknown backend: {backend}")
```

## Common Integration Points

### FastAPI Integration
```python
from fastapi import FastAPI, BackgroundTasks
from google.adk.runners import InMemoryRunner

app = FastAPI()

@app.post("/agents/execute")
async def execute_agent(
    agent_name: str,
    input_data: dict,
    background_tasks: BackgroundTasks
):
    """Execute agent via API."""
    # Load agent specification
    spec = load_agent_spec(agent_name)
    
    # Build agent
    agent = factory.build_agent(spec)
    
    # Create runner
    runner = InMemoryRunner(agent, app_name="api")
    
    # Create session
    session_service = runner.session_service()
    session = session_service.create_session(
        app_name="api",
        user_id="api-user"
    )
    
    # Execute asynchronously
    background_tasks.add_task(
        execute_async,
        runner,
        session,
        input_data
    )
    
    return {"session_id": session.id, "status": "executing"}
```

### Streaming Response Pattern
```python
from fastapi import StreamingResponse
import json

@app.post("/agents/stream")
async def stream_execution(agent_name: str, input_data: dict):
    """Stream agent execution events."""
    
    async def event_generator():
        agent = factory.build_agent(load_agent_spec(agent_name))
        runner = InMemoryRunner(agent, app_name="stream")
        session = create_session(runner)
        
        for event in runner.run_async(session.user_id, session.id, input_data):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## Testing Patterns

### Unit Testing Agents
```python
import pytest
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner

def test_agent_creation():
    """Test agent can be created from spec."""
    agent = LlmAgent(
        name="test-agent",
        model="gemini-2.0-flash",
        instruction="Test instruction"
    )
    assert agent.name == "test-agent"

def test_agent_execution():
    """Test agent executes correctly."""
    agent = create_test_agent()
    runner = InMemoryRunner(agent, app_name="test")
    session = create_test_session(runner)
    
    result = runner.run(
        session.user_id,
        session.id,
        {"input": "test"}
    )
    assert result is not None
```

### Integration Testing
```python
@pytest.mark.integration
async def test_workflow_execution():
    """Test complete workflow execution."""
    template = load_test_template()
    input_data = {"test": "data"}
    
    result = await execute_workflow(template, input_data)
    
    assert result["status"] == "success"
    assert "output" in result
```

## Performance Optimization

### Caching Agent Instances
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_agent(spec_name: str) -> BaseAgent:
    """Cache frequently used agents."""
    spec = load_agent_spec(spec_name)
    return factory.build_agent(spec)
```

### Connection Pooling
```python
# ADK handles connection pooling internally
# Configure via environment variables
os.environ["ADK_MAX_CONNECTIONS"] = "20"
os.environ["ADK_CONNECTION_TIMEOUT"] = "30"
```

### Async Execution
```python
import asyncio

async def execute_parallel_agents(agents: list, input_data: dict):
    """Execute multiple agents in parallel."""
    tasks = []
    for agent in agents:
        runner = InMemoryRunner(agent, app_name="parallel")
        session = create_session(runner)
        
        task = asyncio.create_task(
            execute_agent_async(runner, session, input_data)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Debugging and Monitoring

### Enable Debug Logging
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("google.adk")
logger.setLevel(logging.DEBUG)
```

### Track Execution Metrics
```python
import time

def track_execution(func):
    """Decorator to track execution time."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        log_metric("execution_time", duration)
        return result
    return wrapper

@track_execution
def execute_agent(agent, input_data):
    """Execute agent with metrics."""
    return runner.run(user_id, session_id, input_data)
```

## Security Considerations

### API Key Management
```python
# Use environment variables
os.environ["GEMINI_API_KEY"] = get_secret("gemini-api-key")

# Never hardcode keys
# Never log keys
# Rotate keys regularly
```

### Input Validation
```python
from pydantic import BaseModel, validator

class AgentInput(BaseModel):
    text: str
    options: dict = {}
    
    @validator("text")
    def validate_text(cls, v):
        if len(v) > 10000:
            raise ValueError("Text too long")
        return v
```

### Session Security
```python
import secrets

def create_secure_session():
    """Create session with secure ID."""
    session_id = secrets.token_urlsafe(32)
    return session_service.create_session(
        app_name="secure-app",
        user_id=authenticated_user_id,
        session_id=session_id
    )
```

## Migration Guide

### From Custom Agents to ADK
```python
# Before (Custom)
class CustomAnalyzer:
    def analyze(self, text):
        # Custom logic
        return result

# After (ADK)
analyzer = LlmAgent(
    name="analyzer",
    model="gemini-2.0-flash",
    instruction="Analyze the provided text",
    tools=[analyze_function]
)
```

### From Manual Orchestration to ADK Workflows
```python
# Before (Manual)
result1 = agent1.execute(data)
result2 = agent2.execute(result1)
result3 = agent3.execute(result2)

# After (ADK)
workflow = SequentialAgent(
    name="workflow",
    sub_agents=[agent1, agent2, agent3]
)
result = runner.run(user_id, session_id, data)
```

## Troubleshooting

### Common Issues and Solutions

1. **Import Errors**
   - Ensure `pip install google-adk` completed successfully
   - Check Python version >= 3.9

2. **API Key Issues**
   - Verify GEMINI_API_KEY is set
   - Check key has necessary permissions

3. **Session Errors**
   - Ensure session service is initialized
   - Check session ID format

4. **Tool Execution Failures**
   - Validate function signatures
   - Check parameter types match

5. **Performance Issues**
   - Use async execution for I/O operations
   - Cache frequently used agents
   - Monitor token usage

## References

- Official Docs: https://google.github.io/adk-docs/
- API Reference: https://google.github.io/adk-docs/api-reference/python/
- GitHub: https://github.com/google/adk-python
- Examples: https://github.com/google/adk-python/tree/main/examples