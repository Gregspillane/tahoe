# ADK Dev UI Usage Guide

## Service-Only Operation

The ADK Dev UI operates entirely within the `agent-engine` service directory. All commands must be run from the service directory, not the project root.

## Setup & Usage

### 1. Navigate to Service Directory
```bash
cd services/agent-engine
```

### 2. Basic Commands
```bash
# Validate setup
make dev-ui-validate

# Install ADK and validate
make dev-ui-setup  

# Launch Dev UI
make dev-ui

# Launch in Docker
make dev-ui-docker
```

### 3. Direct Script Usage
```bash
# Validate setup
python3 scripts/launch_dev_ui.py --validate

# Launch with custom port
python3 scripts/launch_dev_ui.py --port 8002

# Launch with debug mode
python3 scripts/launch_dev_ui.py --debug
```

## Docker Setup

### Prerequisites
Infrastructure services must be running:
```bash
cd ../infrastructure
make up
```

### Launch Dev UI in Docker
```bash
cd services/agent-engine
make dev-ui-docker
```

This will:
- Build the Dev UI container
- Connect to `infrastructure_tahoe-network` 
- Expose Dev UI on port 8002
- Mount source code for development

## Access

Once running, the Dev UI is available at:
**http://localhost:8002**

### Features Available
- **Agent Selection**: Dropdown with 6 example agents
- **Interactive Chat**: Text-based agent interaction
- **Events Tab**: Real-time debugging with function call traces
- **Agent Discovery**: Automatic loading from `specs/agents/`

## Troubleshooting

### Wrong Directory Error
```
❌ Prerequisites not met:
   - Please run from the agent-engine service directory: cd services/agent-engine
```
**Solution**: Change to the agent-engine service directory

### Port Conflict
The Dev UI uses port 8002 (not 8000) to avoid conflicts with other services.

### GEMINI_API_KEY Missing
Set your API key in the root `.env` file:
```bash
GEMINI_API_KEY=your_key_here
```

## Architecture

The Dev UI is completely self-contained within the agent-engine service:
- **Specs**: `specs/agents/` (6 example agents)
- **Scripts**: `scripts/launch_dev_ui.py`
- **Docker**: `docker-compose.dev-ui.yml` + `Dockerfile.dev-ui`
- **Network**: Uses `infrastructure_tahoe-network` for service communication

This aligns with the monorepo principle where each service operates independently while sharing centralized configuration.