#!/bin/bash
set -e

# Build script for Tahoe Agent Engine with centralized configuration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVICE_DIR="$SCRIPT_DIR"

echo "Building Tahoe Agent Engine..."
echo "Project root: $PROJECT_ROOT"
echo "Service directory: $SERVICE_DIR"

# Check if root .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✓ Found centralized .env file"
    # Copy .env to service directory for Docker build context
    cp "$PROJECT_ROOT/.env" "$SERVICE_DIR/.env.build"
    echo "✓ Copied .env to build context"
else
    echo "⚠ No .env file found at $PROJECT_ROOT/.env"
    echo "  Creating minimal .env for build..."
    cat > "$SERVICE_DIR/.env.build" << EOF
ENVIRONMENT=production
GEMINI_API_KEY=placeholder
ADK_DEFAULT_MODEL=gemini-2.0-flash
EOF
fi

# Build Docker image
echo "Building Docker image..."
cd "$SERVICE_DIR"

# Update Dockerfile to use the copied .env
if [ -f ".env.build" ]; then
    # Temporarily modify Dockerfile to copy .env
    sed -i.bak 's|# Note: .env file will be mounted in development|COPY --chown=appuser:appuser .env.build ./.env|' Dockerfile
fi

docker build -t tahoe-agent-engine:latest .

# Restore Dockerfile
if [ -f "Dockerfile.bak" ]; then
    mv Dockerfile.bak Dockerfile
fi

# Clean up temporary .env
if [ -f ".env.build" ]; then
    rm ".env.build"
fi

echo "✓ Build complete: tahoe-agent-engine:latest"
echo ""
echo "Usage:"
echo "  Start infrastructure: cd ../infrastructure && make up"
echo "  Development: make dev (native) or use infrastructure docker-compose"
echo "  Production: docker run -p 8001:8001 tahoe-agent-engine:latest"