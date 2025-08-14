
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tahoe** is a universal agent orchestration service built on Google's Agent Development Kit (ADK). It provides a configuration-driven REST API for creating, managing, and executing AI agents, abstracting ADK complexity behind a clean interface.

## Common Development Commands

### Local Development
```bash
# Start API server
python run_local.py server

# Run usage example
python run_local.py example

# Install dependencies
pip install -r requirements.txt
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access API at http://localhost:9000
# API docs at http://localhost:9000/docs
```

### Environment Setup
Required environment variables:
- `GOOGLE_API_KEY` - Google AI API key for Gemini models
- `TAHOE_SERVICE_TOKEN` - Service authentication token

## Core Architecture

### Service Structure
- **FastAPI REST API** (`src/tahoe/api/`) - External interface with authentication
- **Agent Factory** (`src/tahoe/core/agent_factory.py`) - Creates ADK agents from configurations
- **Config Loader** (`src/tahoe/core/config_loader.py`) - Loads and validates YAML/JSON agent specs
- **Templates** (`src/tahoe/templates/`) - Reusable agent and workflow definitions

### Agent Types Supported
- **LLM Agents** - Single model interactions
- **Sequential Agents** - Multi-step workflows 
- **Parallel Agents** - Concurrent execution
- **Loop Agents** - Iterative workflows

### API Endpoints
- `POST /agents` - Create agent from configuration
- `POST /agents/{id}/execute` - Execute agent with input
- `POST /sessions` - Create conversation session
- `GET /sessions/{id}` - Get session information

## Critical: ADK Documentation Requirements

### Context
**Claude has zero training on Google ADK** - it was released after training cutoff.

### Documentation Location
- **Local ADK Documentation**: `/adk_docs_markdown/` contains complete ADK docs
  - Use `_SUMMARY.md` for navigation
  - Python API Reference: `/adk_docs_markdown/api-reference_python.md`
  - Quick Start: `/adk_docs_markdown/get-started_quickstart.md`
  - **Always reference these local docs before implementing ADK features**

## Development Principles

### KISS (Keep It Simple, Stupid)
- Simple implementations over complex abstractions
- Minimal viable features first, iterate based on needs
- Clear, readable code over compact code
- Explicit over implicit - make intentions obvious

### Standards
- Fail fast with clear, actionable error messages
- Local environment should mirror production
- Prioritize code quality over backwards compatibility (pre-launch)

## Memory Bank System
- **Active context**: `/memory-bank/` - Living project documents
  - `context.md` - Session handoffs and current state
  - `architecture.md` - Technical patterns and decisions  
  - `progress.md` - Development status tracking
  - `decisions.md` - Key project decisions log
- **Archived docs**: `/memory-bank/archive/` - Completed plans

## Configuration System

### Agent Templates
Pre-built configurations in `src/tahoe/templates/`:
- `agents/simple_assistant.yaml` - Basic LLM assistant
- `workflows/research_workflow.yaml` - Multi-step research workflow

### Example Agent Configuration
```yaml
name: SimpleAssistant
type: llm
description: A helpful AI assistant
config:
  model: gemini-2.5-flash-lite
  instruction: "You are a helpful AI assistant..."
  output_key: response
```

## Testing and Development

### Basic Testing
No formal test framework yet - use the example script:
```bash
python run_local.py example
```

### Service Authentication
All API endpoints require Bearer token:
- Development token: `development_token_change_in_production`
- Production: Set `TAHOE_SERVICE_TOKEN` environment variable