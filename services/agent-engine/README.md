# Agent Engine Service

Universal agent orchestration platform built with Google ADK and FastAPI.

**Service Independence**: This service is designed to be deployed independently on its own DNS/domain, as part of the Tahoe monorepo architecture.

## Quick Start

### Prerequisites
- Python 3.9+ (Python 3.12 recommended)
- Docker and Docker Compose
- Infrastructure services running (PostgreSQL, Redis)
- Google Gemini API key

### Development Setup

1. **Start Infrastructure Services**:
```bash
# From the infrastructure directory
cd ../infrastructure
make up
```

2. **Install Service Dependencies**:
```bash
# From this service directory
make install
```

3. **Configure Environment**:
   - Root-level `.env` file provides centralized configuration
   - Set your `GEMINI_API_KEY` in the root `.env` file
   - Configuration is automatically mounted in development

4. **Validate Setup**:
```bash
make validate  # Validates ADK patterns
make test      # Runs unit tests
```

5. **Start Development Server**:
```bash
make dev  # Starts with hot reload on port 8001
```

### Service Commands

```bash
# Service management
make help        # Show all available commands
make install     # Install dependencies
make test        # Run unit tests
make validate    # Validate ADK compliance
make dev         # Start development server
make run         # Start production server

# Docker service deployment
make docker-up   # Start service in Docker
make docker-down # Stop Docker service
make docker-logs # View service logs

# Health and cleanup
make health      # Check service health
make clean       # Clean Python cache
```

## Monorepo Architecture

### Service Independence
- **Self-Contained**: All service-specific code and configuration
- **External Dependencies**: Connects to shared infrastructure services
- **Separate Deployment**: Can be deployed to its own DNS/domain
- **Network Communication**: Uses Docker networks to communicate with infrastructure

### Directory Structure
```
services/agent-engine/
├── src/                    # Service source code
│   ├── main.py            # FastAPI application
│   └── ...
├── config/                 # Service-specific configuration
├── tests/                  # Service tests
├── specs/                  # Agent specifications
├── examples/               # Usage examples
├── docker-compose.yml      # Service Docker configuration
├── Dockerfile             # Service container
├── Makefile               # Service commands
└── requirements.txt       # Service dependencies
```

### Configuration System
- **Centralized**: Root-level `.env` file for all configuration
- **Environment-Aware**: Supports development/staging/production
- **Service-Scoped**: Uses `AGENT_ENGINE_*` prefixed variables
- **ADK Integration**: Gemini API keys via environment variables

## API Endpoints

- `GET /health` - Service health check with ADK status
- `GET /config` - Configuration endpoint (development only)

## ADK Integration

This service is **ADK-compliant** with validated patterns:
- ✅ **Agent Naming**: Uses valid Python identifiers
- ✅ **Session Access**: Property-based session service access
- ✅ **Agent Types**: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
- ✅ **Tool Integration**: Automatic and explicit tool wrapping
- ✅ **Model Configuration**: Runtime parameter handling

See `scripts/validate_adk_patterns.py` for comprehensive validation.

## Architecture

### Core Components
- **FastAPI**: Async REST API framework
- **Google ADK**: Universal agent orchestration
- **Centralized Config**: Environment-aware configuration system
- **Specification System**: YAML/JSON-driven agent definitions

### External Dependencies
- **PostgreSQL**: Data persistence (via infrastructure service)
- **Redis**: Caching and session state (via infrastructure service)
- **Nginx**: Load balancing and TLS (via infrastructure service)

### Model Support
- **Primary**: Gemini models via ADK
- **Fallback**: Configurable model fallback strategies
- **Future**: Multi-provider support planned

## Development

### Testing
```bash
make test                    # Unit tests
make test-integration       # ADK integration tests
python scripts/verify_adk.py # Verify ADK components
```

### Validation
```bash
make validate  # Comprehensive ADK pattern validation
# Reports: 7/8 validation checks passing (production ready)
```

### Examples
See `examples/` directory for:
- Basic agent creation
- Workflow orchestration
- Tool integration patterns

## Production Deployment

### Docker Deployment
1. **Build Service Image**:
```bash
make build
```

2. **Deploy with Infrastructure**:
```bash
# Start infrastructure first
cd ../infrastructure && make up

# Then start this service
make docker-up
```

### Environment Configuration
- **Development**: Uses root `.env` file
- **Production**: Uses environment variables from Helm/Vault
- **Configuration Validation**: Strict validation in production

### Health Monitoring
- Health endpoint: `/health`
- ADK component status included
- Docker healthchecks configured
- Prometheus metrics ready (future)

## Troubleshooting

### Common Issues
1. **Service Won't Start**: Check infrastructure services are running
2. **ADK Validation Fails**: Run `make validate` for detailed report
3. **API Key Issues**: Verify `GEMINI_API_KEY` in root `.env`

### Debug Commands
```bash
make health              # Check service status
make docker-logs        # View detailed logs
cd ../infrastructure && make logs  # Check infrastructure
```

### Support
- Configuration issues: Check centralized `.env` file
- ADK issues: Run validation scripts
- Service issues: Check Docker logs and health endpoint