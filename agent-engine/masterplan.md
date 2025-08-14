# Agent-Engine Service - Progressive Development Masterplan

**Version**: 3.0  
**Date**: August 2025  
**Status**: Progressive Local Development
**Approach**: Start Simple, Build Incrementally

---

## Executive Summary

This masterplan follows a **progressive development approach** aligned with ADK documentation patterns. We start with the simplest possible working agent using ADK's Dev UI, then incrementally add features, complexity, and custom API layers. Each phase builds upon working code from the previous phase.

---

## Development Philosophy

### Core Principles
1. **Start with ADK's Quickstart** - Get a basic agent running in minutes
2. **Use Dev UI First** - Test and validate agents before adding API layers
3. **Incremental Complexity** - Add one feature at a time
4. **Document as You Build** - Keep notes on what works
5. **Test at Every Step** - Ensure each phase works before proceeding

### What We're NOT Doing
- ❌ Building complex multi-agent systems on day one
- ❌ Creating custom API layers before agents work
- ❌ Writing authentication middleware before basic functionality
- ❌ Setting up databases before we have working agents
- ❌ Attempting deployment configurations early

---

## Phase 1: Foundation (Day 1-2)
**Goal: Get ADK installed and a basic agent running with Dev UI**

### 1.1 Environment Setup

According to `get-started/installation/` documentation:

```bash
# Create project directory
mkdir agent-engine
cd agent-engine

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate.bat

# Install ADK
pip install google-adk
```

### 1.2 Create Your First Agent

Following `get-started/quickstart/` pattern:

```bash
# Create agent directory structure
mkdir simple_qa_agent
touch simple_qa_agent/__init__.py
touch simple_qa_agent/agent.py
```

**simple_qa_agent/__init__.py:**
```python
from . import agent
```

**simple_qa_agent/agent.py:**
```python
from google.adk.agents import Agent

# Start with the simplest possible agent
root_agent = Agent(
    name="simple_qa_agent",
    model="gemini-2.5-flash-lite",
    instruction="You are a helpful QA assistant that analyzes call transcripts."
)
```

### 1.3 Configure API Keys

Create `.env` file:
```bash
# .env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-actual-api-key-here
```

### 1.4 Test with Dev UI

According to `get-started/quickstart/` documentation:

```bash
# Launch Dev UI (from parent directory)
adk web

# Access at http://localhost:8000
# Select "simple_qa_agent" from dropdown
# Test with basic queries
```

**Success Criteria:**
- ✅ Agent appears in Dev UI dropdown
- ✅ Agent responds to basic queries
- ✅ Can view Events and Trace tabs

---

## Phase 2: Add Basic QA Functionality (Day 3-4)
**Goal: Create a simple compliance checking tool**

### 2.1 Add First Custom Tool

Update **simple_qa_agent/agent.py:**

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def check_fdcpa_compliance(transcript: str) -> dict:
    """
    Basic FDCPA compliance check.
    
    Args:
        transcript: The call transcript to analyze
        
    Returns:
        Compliance check results
    """
    violations = []
    
    # Simple keyword-based checks (to be enhanced later)
    forbidden_phrases = [
        "arrest", "jail", "wage garnishment", 
        "lawsuit" # without proper disclosure
    ]
    
    for phrase in forbidden_phrases:
        if phrase.lower() in transcript.lower():
            violations.append(f"Potential violation: mention of '{phrase}'")
    
    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "checked_items": ["FDCPA basic keywords"]
    }

# Create tool
compliance_tool = FunctionTool(
    func=check_fdcpa_compliance,
    description="Check transcript for FDCPA compliance violations"
)

# Update agent with tool
root_agent = Agent(
    name="simple_qa_agent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a QA specialist analyzing call transcripts for compliance.
    When given a transcript, use the compliance checking tool to identify any violations.""",
    tools=[compliance_tool]
)
```

### 2.2 Test in Dev UI

1. Restart `adk web`
2. Paste a sample transcript
3. Verify tool execution in Events tab
4. Check Trace for performance

**Success Criteria:**
- ✅ Tool appears in agent capabilities
- ✅ Tool executes when transcript provided
- ✅ Results display correctly

---

## Phase 3: Multi-Agent Workflow (Day 5-6)
**Goal: Create a sequential workflow for complete QA analysis**

### 3.1 Create Agent Hierarchy

Create new directory structure:
```bash
mkdir qa_workflow
touch qa_workflow/__init__.py
touch qa_workflow/agent.py
```

**qa_workflow/agent.py:**

```python
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.tools import FunctionTool

# Agent 1: Extract metadata
metadata_agent = LlmAgent(
    name="metadata_extractor",
    model="gemini-2.5-flash-lite",
    instruction="""Extract the following from the transcript:
    - Agent name
    - Customer name (if mentioned)
    - Call date/time
    - Main topic of call
    Format as JSON.""",
    output_key="metadata"
)

# Agent 2: Check compliance
def check_compliance(transcript: str) -> dict:
    """Check for FDCPA violations"""
    # Implementation from Phase 2
    return {"violations": [], "compliant": True}

compliance_agent = LlmAgent(
    name="compliance_checker",
    model="gemini-2.5-flash-lite",
    instruction="Use the tool to check compliance: {transcript}",
    tools=[FunctionTool(check_compliance)],
    output_key="compliance_results"
)

# Agent 3: Generate scorecard
scorecard_agent = LlmAgent(
    name="scorecard_generator",
    model="gemini-2.5-flash-lite",
    instruction="""Based on the metadata and compliance results, generate a scorecard:
    
    Metadata: {metadata}
    Compliance: {compliance_results}
    
    Include:
    - Overall score (0-100)
    - Key findings
    - Recommendations""",
    output_key="scorecard"
)

# Main workflow agent
root_agent = SequentialAgent(
    name="qa_workflow",
    description="Complete QA analysis workflow",
    sub_agents=[
        metadata_agent,
        compliance_agent,
        scorecard_agent
    ]
)
```

### 3.2 Test Workflow in Dev UI

1. Launch with `adk web`
2. Select "qa_workflow" agent
3. Provide sample transcript
4. Verify all three agents execute in sequence
5. Check output keys in session state

**Success Criteria:**
- ✅ All agents execute in order
- ✅ Data passes between agents via output_key
- ✅ Final scorecard generated

---

## Phase 4: Add Session & State Management (Day 7-8)
**Goal: Enable persistent sessions for QA results**

### 4.1 Create Test Script with Sessions

**test_with_sessions.py:**

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Content, Part
from qa_workflow.agent import root_agent
import asyncio

async def test_qa_with_sessions():
    """Test QA workflow with session management"""
    
    # Initialize session service
    session_service = InMemorySessionService()
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name="qa_system",
        session_service=session_service
    )
    
    # Create session with initial state
    session = await session_service.create_session(
        app_name="qa_system",
        user_id="qa_tester",
        state={
            "client": "TestClient",
            "date": "2025-08-14"
        }
    )
    
    # Sample transcript
    transcript = """
    Agent: Thank you for calling. My name is John.
    Customer: Hi, I received a call about my account.
    Agent: Yes, I'm calling about your past due balance.
    Customer: I can't pay right now.
    Agent: I understand. Let's discuss payment options.
    """
    
    # Run the workflow
    content = Content.from_parts(Part.from_text(f"Analyze this transcript: {transcript}"))
    
    events = []
    async for event in runner.run_async(
        session.user_id,
        session.id,
        content
    ):
        events.append(event)
        print(f"Event: {event.type}")
    
    # Get final session state
    final_session = await session_service.get_session(
        app_name="qa_system",
        user_id="qa_tester",
        session_id=session.id
    )
    
    print("\nFinal State:")
    print(f"Metadata: {final_session.state.get('metadata')}")
    print(f"Compliance: {final_session.state.get('compliance_results')}")
    print(f"Scorecard: {final_session.state.get('scorecard')}")

if __name__ == "__main__":
    asyncio.run(test_qa_with_sessions())
```

### 4.2 Run Session Test

```bash
python test_with_sessions.py
```

**Success Criteria:**
- ✅ Session created successfully
- ✅ State persists between agent calls
- ✅ Can retrieve results from session

---

## Phase 5: Add API Layer (Day 9-10)
**Goal: Create REST API endpoints for the QA system**

### 5.1 Create FastAPI Application

**main.py:**

```python
import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import Header, HTTPException
from pydantic import BaseModel
from qa_workflow.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Content, Part

# Get base FastAPI app from ADK
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
app = get_fast_api_app(
    agent_dir=AGENT_DIR,
    allow_origins=["http://localhost:*"]
)

# Initialize services
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="qa_system",
    session_service=session_service
)

# Custom endpoint models
class TranscriptAnalysisRequest(BaseModel):
    transcript: str
    client_id: str
    call_id: str

class AnalysisResponse(BaseModel):
    session_id: str
    compliance_score: dict
    scorecard: dict

# Custom QA endpoint
@app.post("/qa/analyze", response_model=AnalysisResponse)
async def analyze_transcript(request: TranscriptAnalysisRequest):
    """Analyze a transcript for QA"""
    
    # Create session
    session = await session_service.create_session(
        app_name="qa_system",
        user_id="api_user",
        state={
            "client_id": request.client_id,
            "call_id": request.call_id
        }
    )
    
    # Run analysis
    content = Content.from_parts(
        Part.from_text(f"Analyze this transcript: {request.transcript}")
    )
    
    async for event in runner.run_async(session.user_id, session.id, content):
        pass  # Process events
    
    # Get results
    final_session = await session_service.get_session(
        app_name="qa_system",
        user_id="api_user",
        session_id=session.id
    )
    
    return AnalysisResponse(
        session_id=session.id,
        compliance_score=final_session.state.get("compliance_results", {}),
        scorecard=final_session.state.get("scorecard", {})
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "qa_system"}
```

### 5.2 Test API

```bash
# Terminal 1: Start the API server
uvicorn main:app --reload --port 9000

# Terminal 2: Test with curl
curl -X POST http://localhost:9000/qa/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Agent: Hello, this is about your account...",
    "client_id": "client123",
    "call_id": "call456"
  }'
```

**Success Criteria:**
- ✅ API server starts on port 9000
- ✅ Health check returns 200
- ✅ Analysis endpoint processes transcript
- ✅ Returns structured QA results

---

## Phase 6: Add Database Persistence (Day 11-12)
**Goal: Store QA results in PostgreSQL**

### 6.1 Setup Docker Compose

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: agentengine
      POSTGRES_PASSWORD: localdev123
      POSTGRES_DB: agentengine_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 6.2 Install Prisma

```bash
pip install prisma
```

### 6.3 Create Schema

**schema.prisma:**

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-py"
}

model QAResult {
  id            String   @id @default(uuid())
  sessionId     String
  callId        String
  clientId      String
  transcript    String   @db.Text
  scorecard     Json
  compliance    Json
  createdAt     DateTime @default(now())
  
  @@index([sessionId])
  @@index([clientId])
}
```

### 6.4 Initialize Database

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Set DATABASE_URL in .env
echo "DATABASE_URL=postgresql://agentengine:localdev123@localhost:5432/agentengine_db" >> .env

# Generate Prisma client
prisma generate

# Push schema to database
prisma db push
```

### 6.5 Update API to Save Results

Add to **main.py:**

```python
from prisma import Prisma

# Initialize Prisma
prisma = Prisma()

@app.on_event("startup")
async def startup():
    await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

# Update analyze_transcript endpoint
@app.post("/qa/analyze")
async def analyze_transcript(request: TranscriptAnalysisRequest):
    # ... existing code ...
    
    # Save to database
    qa_result = await prisma.qaresult.create(
        data={
            "sessionId": session.id,
            "callId": request.call_id,
            "clientId": request.client_id,
            "transcript": request.transcript,
            "scorecard": final_session.state.get("scorecard", {}),
            "compliance": final_session.state.get("compliance_results", {})
        }
    )
    
    return AnalysisResponse(
        session_id=session.id,
        compliance_score=final_session.state.get("compliance_results", {}),
        scorecard=final_session.state.get("scorecard", {})
    )
```

**Success Criteria:**
- ✅ Database connection established
- ✅ QA results saved to PostgreSQL
- ✅ Can query saved results

---

## Phase 7: Client-Specific Configuration (Day 13-14)
**Goal: Add dynamic client configuration**

### 7.1 Add Client Config to Database

Update **schema.prisma:**

```prisma
model ClientConfig {
  id                String   @id @default(uuid())
  clientId          String   @unique
  complianceRules   Json
  scoringWeights    Json
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt
}
```

### 7.2 Create Dynamic Compliance Tool

```python
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

async def dynamic_compliance_check(transcript: str, tool_context: ToolContext) -> dict:
    """Check compliance based on client configuration"""
    
    # Get client from session state
    client_id = tool_context.state.get("client_id")
    
    # Load client config from database
    config = await prisma.clientconfig.find_unique(
        where={"clientId": client_id}
    )
    
    if config:
        rules = config.complianceRules
        # Apply client-specific rules
    else:
        # Use default rules
        rules = {"forbidden_phrases": ["arrest", "jail"]}
    
    violations = []
    for phrase in rules.get("forbidden_phrases", []):
        if phrase in transcript.lower():
            violations.append(f"Found: {phrase}")
    
    return {
        "client": client_id,
        "violations": violations,
        "rules_applied": len(rules.get("forbidden_phrases", []))
    }
```

**Success Criteria:**
- ✅ Client configs stored in database
- ✅ Tools adapt based on client
- ✅ Different results for different clients

---

## Phase 8: Authentication (Day 15)
**Goal: Add simple service token authentication**

### 8.1 Add Authentication Middleware

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Simple token verification"""
    token = credentials.credentials
    
    # In production, verify JWT properly
    if token != os.getenv("SERVICE_TOKEN", "dev-token-123"):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

# Protected endpoint
@app.post("/qa/analyze")
async def analyze_transcript(
    request: TranscriptAnalysisRequest,
    token: str = Security(verify_token)
):
    # ... existing code ...
```

**Success Criteria:**
- ✅ Endpoints require authentication
- ✅ Invalid tokens rejected
- ✅ Dev UI still accessible

---

## Phase 9: Complete Docker Setup (Day 16)
**Goal: Containerize the entire application**

### 9.1 Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Generate Prisma client
RUN prisma generate

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
```

### 9.2 Update docker-compose.yml

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: agentengine
      POSTGRES_PASSWORD: localdev123
      POSTGRES_DB: agentengine_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  agent-engine:
    build: .
    ports:
      - "9000:9000"  # API
      - "9001:9001"  # Dev UI
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=postgresql://agentengine:localdev123@postgres:5432/agentengine_db
      - SERVICE_TOKEN=${SERVICE_TOKEN}
    depends_on:
      - postgres
    volumes:
      - ./:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 9000

volumes:
  postgres_data:
```

### 9.3 Run Complete System

```bash
# Build and start all services
docker-compose up --build

# In another terminal, initialize database
docker-compose exec agent-engine prisma db push
```

**Success Criteria:**
- ✅ All services start via Docker Compose
- ✅ API accessible at localhost:9000
- ✅ Database connections work
- ✅ Hot reload works for development

---

## Phase 10: Testing & Documentation (Day 17-18)
**Goal: Add comprehensive testing and documentation**

### 10.1 Create Test Suite

**tests/test_qa_workflow.py:**

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_transcript():
    response = client.post(
        "/qa/analyze",
        json={
            "transcript": "Test transcript",
            "client_id": "test_client",
            "call_id": "test_call"
        },
        headers={"Authorization": "Bearer dev-token-123"}
    )
    assert response.status_code == 200
    assert "session_id" in response.json()
```

### 10.2 Run Tests

```bash
pytest tests/
```

### 10.3 Create Documentation

**docs/LOCAL_SETUP.md:**

```markdown
# Local Development Setup

## Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Google API Key (for Gemini)

## Quick Start

1. Clone repository
2. Copy .env.example to .env and add your API keys
3. Run: `docker-compose up`
4. Access API at http://localhost:9000
5. Access Dev UI at http://localhost:9001

## Testing Agents

Use the Dev UI to test individual agents:
1. Navigate to http://localhost:9001
2. Select agent from dropdown
3. Test with sample transcripts
```

**Success Criteria:**
- ✅ Tests pass
- ✅ Documentation complete
- ✅ README includes setup instructions

---

## Next Steps & Future Enhancements

Once all phases are complete and stable:

1. **Performance Optimization**
   - Add caching for client configs
   - Implement connection pooling
   - Optimize database queries

2. **Advanced Features**
   - Real-time streaming analysis
   - Batch processing endpoints
   - Webhook notifications

3. **Production Readiness**
   - Add comprehensive logging
   - Implement monitoring/metrics
   - Create deployment manifests
   - Add rate limiting

4. **Enhanced QA Logic**
   - ML-based violation detection
   - Sentiment analysis
   - Custom scoring algorithms

---

## Development Checklist

### Phase 1 ✅
- [ ] Install ADK
- [ ] Create first agent
- [ ] Test with Dev UI
- [ ] Verify agent responds

### Phase 2 ✅
- [ ] Add compliance tool
- [ ] Test tool execution
- [ ] Verify results in Dev UI

### Phase 3 ✅
- [ ] Create workflow agents
- [ ] Test sequential execution
- [ ] Verify data flow

### Phase 4 ✅
- [ ] Add session management
- [ ] Test state persistence
- [ ] Verify session retrieval

### Phase 5 ✅
- [ ] Create FastAPI app
- [ ] Add custom endpoints
- [ ] Test API responses

### Phase 6 ✅
- [ ] Setup PostgreSQL
- [ ] Create Prisma schema
- [ ] Test data persistence

### Phase 7 ✅
- [ ] Add client configs
- [ ] Test dynamic rules
- [ ] Verify client-specific results

### Phase 8 ✅
- [ ] Add authentication
- [ ] Test token validation
- [ ] Verify security

### Phase 9 ✅
- [ ] Create Dockerfile
- [ ] Setup Docker Compose
- [ ] Test containerized app

### Phase 10 ✅
- [ ] Write tests
- [ ] Create documentation
- [ ] Final validation

---

## Success Metrics

By the end of this progressive development:

1. **Working System**: Complete QA analysis system running locally
2. **Tested Components**: Each phase validated before proceeding
3. **Documentation**: Clear setup and usage instructions
4. **Scalable Architecture**: Ready for production enhancements
5. **ADK Best Practices**: Following documented patterns throughout

---

## Important Reminders

1. **Always check ADK documentation** before implementing features
2. **Test in Dev UI first** before adding API complexity
3. **Keep each phase simple** - complexity comes later
4. **Document what works** - maintain a development log
5. **Don't skip phases** - each builds on the previous

---

*This progressive approach ensures a stable, working system at each phase while gradually building toward the complete QA analysis platform.*