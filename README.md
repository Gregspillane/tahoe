# Project Tahoe

Universal Agent Orchestration Service built on Google's Agent Development Kit (ADK).

## Overview

Tahoe provides a configuration-driven API for creating, managing, and executing AI agents. It abstracts the complexity of ADK behind a clean REST interface, enabling rapid development of agent-powered applications.

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (optional)
- Google API key for Gemini models

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   export GOOGLE_API_KEY="your_google_api_key_here"
   export TAHOE_SERVICE_TOKEN="your_secure_token_here"
   ```

3. **Run the API server:**
   ```bash
   python run_local.py server
   ```

4. **Test with example:**
   ```bash
   # In another terminal
   python run_local.py example
   ```

### Docker Development

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **API will be available at:** `http://localhost:9000`

## API Usage

### Create an Agent

```bash
curl -X POST "http://localhost:9000/agents" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_assistant",
    "type": "llm",
    "config": {
      "model": "gemini-2.0-flash",
      "instruction": "You are a helpful assistant."
    }
  }'
```

### Execute an Agent

```bash
curl -X POST "http://localhost:9000/agents/my_assistant/execute" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my_assistant",
    "input": "What is the capital of France?"
  }'
```

## Configuration

### Agent Templates

Pre-built agent configurations are available in `src/tahoe/templates/`:

- `agents/simple_assistant.yaml` - Basic LLM assistant
- `workflows/research_workflow.yaml` - Multi-step research workflow

### Environment Variables

- `GOOGLE_API_KEY` - Google AI API key
- `TAHOE_SERVICE_TOKEN` - Service authentication token
- `CORS_ORIGINS` - Allowed CORS origins (default: *)

## Architecture

Tahoe is built on these core components:

- **Agent Factory**: Creates ADK agents from configurations
- **Config Loader**: Loads and validates agent specifications
- **API Layer**: REST endpoints for external integration
- **Templates**: Reusable agent and workflow definitions

## Documentation

- API Documentation: `http://localhost:9000/docs` (when running)
- ADK Documentation: `/adk_docs_markdown/` (local copy)
- Project Plan: `MASTERPLAN.md`

## Development

### Project Structure

```
tahoe/
├── src/tahoe/
│   ├── api/                # REST API layer
│   ├── core/               # Core orchestration logic
│   ├── templates/          # Agent templates
│   └── utils/              # Helper utilities
├── examples/               # Usage examples
├── config/                 # Configuration schemas
└── adk_docs_markdown/      # Local ADK documentation
```

### Next Steps

1. ✅ Basic API structure
2. 🔄 POC implementation and testing
3. 🎯 Tool integration
4. 🎯 Advanced workflow patterns
5. 🎯 Production readiness

## License

TBD