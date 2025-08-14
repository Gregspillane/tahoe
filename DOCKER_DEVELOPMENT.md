# Docker Development Guide

This guide covers running Tahoe entirely in Docker for development.

## Quick Start

### 1. Start Tahoe Service

```bash
# Build and start the main service
docker-compose up --build tahoe

# Or run in background
docker-compose up -d --build tahoe
```

The API will be available at: **http://localhost:9000**

### 2. API Documentation

Once running, visit: **http://localhost:9000/docs** for interactive API documentation.

### 3. Test the Service

```bash
# Health check
curl http://localhost:9000/health

# Root endpoint
curl http://localhost:9000/

# Create an agent (requires authentication)
curl -X POST "http://localhost:9000/agents" \
  -H "Authorization: Bearer development_token_change_in_production" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_assistant",
    "type": "llm",
    "config": {
      "model": "gemini-2.5-flash-lite",
      "instruction": "You are a helpful assistant."
    }
  }'

# Execute the agent
curl -X POST "http://localhost:9000/agents/test_assistant/execute" \
  -H "Authorization: Bearer development_token_change_in_production" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test_assistant",
    "input": "What is 2+2?"
  }'
```

## Development Commands

### Main Development Service

```bash
# Start with logs
docker-compose up tahoe

# Start in background
docker-compose up -d tahoe

# View logs
docker-compose logs -f tahoe

# Stop
docker-compose down
```

### Development Tools Container

For running examples or debugging:

```bash
# Start tools container
docker-compose --profile tools up -d tahoe-tools

# Run example inside container
docker-compose exec tahoe-tools python examples/basic_usage.py

# Interactive shell
docker-compose exec tahoe-tools bash

# Python shell
docker-compose exec tahoe-tools python

# Stop tools
docker-compose --profile tools down
```

### Force Rebuild

```bash
# Rebuild containers
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build --force-recreate
```

## Configuration

### Environment Variables

The following are pre-configured in docker-compose.yml:

- `GOOGLE_API_KEY`: Set to your development key
- `TAHOE_SERVICE_TOKEN`: Set to development token
- `GOOGLE_GENAI_USE_VERTEXAI`: FALSE (uses Google AI)
- `ADK_LOG_LEVEL`: INFO
- `CORS_ORIGINS`: * (all origins)

### Volume Mounts

The container mounts these directories for live development:

- `./src` → `/app/src` (code changes reload automatically)
- `./config` → `/app/config` (configuration files)
- `./examples` → `/app/examples` (example scripts)
- `./adk_docs_markdown` → `/app/adk_docs_markdown` (documentation)

### Hot Reload

The service runs with `--reload` flag, so changes to Python files will automatically restart the server.

## Health Monitoring

Health check is configured to test the `/health` endpoint every 30 seconds.

Check health status:
```bash
docker-compose ps
```

## Logs and Debugging

### View Real-time Logs
```bash
docker-compose logs -f tahoe
```

### Debug with Interactive Shell
```bash
# Start tools container
docker-compose --profile tools up -d tahoe-tools

# Get interactive shell
docker-compose exec tahoe-tools bash

# Run Python REPL with full environment
docker-compose exec tahoe-tools python
```

## Example Workflows

### Test Agent Creation
```bash
# Inside the tools container
docker-compose exec tahoe-tools python -c "
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        # Test health
        r = await client.get('http://tahoe:9000/health')
        print(f'Health: {r.json()}')
        
        # Create agent
        r = await client.post(
            'http://tahoe:9000/agents',
            headers={'Authorization': 'Bearer development_token_change_in_production'},
            json={
                'name': 'test_agent',
                'type': 'llm',
                'config': {'model': 'gemini-2.5-flash-lite', 'instruction': 'Be helpful'}
            }
        )
        print(f'Agent created: {r.json()}')

asyncio.run(test())
"
```

### Run Full Example
```bash
# Modify examples/basic_usage.py to use internal hostname
docker-compose exec tahoe-tools sed -i 's/localhost:9000/tahoe:9000/g' examples/basic_usage.py

# Run the example
docker-compose exec tahoe-tools python examples/basic_usage.py
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs tahoe

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use
```bash
# Check what's using port 9000
lsof -i :9000

# Or change port in docker-compose.yml
# ports:
#   - "9001:9000"  # Use port 9001 instead
```

### Permission Issues
```bash
# Fix permissions on host
sudo chown -R $USER:$USER .
```

This setup provides a complete Docker-based development environment with hot reload, health monitoring, and debugging capabilities.