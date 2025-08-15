#!/bin/bash

# Tahoe Services Startup Script
# This script provides an easy way to start all services in the correct order

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for service health
wait_for_service() {
    local service_name=$1
    local health_check=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be healthy..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval $health_check >/dev/null 2>&1; then
            print_success "$service_name is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to become healthy after $max_attempts attempts"
    return 1
}

# Change to project root directory
cd "$(dirname "$0")/.."

print_status "Starting Tahoe services..."

# Start infrastructure
print_status "Starting infrastructure services (PostgreSQL + Redis)..."
cd infrastructure && docker-compose up -d
cd ..

# Wait for PostgreSQL
wait_for_service "PostgreSQL" "docker exec tahoe-postgres pg_isready -U tahoe_user -d tahoe"

# Wait for Redis
wait_for_service "Redis" "docker exec tahoe-redis redis-cli ping"

print_success "Infrastructure is ready"

# Start transcription service
print_status "Starting transcription service..."
cd transcribe && docker-compose up -d
cd ..

# Wait for transcription service
wait_for_service "Transcription Service" "curl -f -s http://localhost:9100/health"

print_success "All services are running!"

# Show service status
print_status "Service Status:"
echo ""
echo "Infrastructure:"
cd infrastructure && docker-compose ps
cd ..

echo ""
echo "Transcription Service:"
cd transcribe && docker-compose ps
cd ..

echo ""
print_status "Quick connectivity test:"
echo "PostgreSQL: $(docker exec tahoe-postgres psql -U tahoe_user -d tahoe -c 'SELECT 1' -t 2>/dev/null | tr -d ' \n' || echo 'FAILED')"
echo "Redis: $(docker exec tahoe-redis redis-cli ping 2>/dev/null || echo 'FAILED')"
echo "API Health: $(curl -s http://localhost:9100/health | grep -o '"status":"[^"]*"' || echo 'FAILED')"

echo ""
print_success "Setup complete! Services are available at:"
echo "  - Transcription API: http://localhost:9100"
echo "  - PostgreSQL: localhost:5432 (tahoe database)"
echo "  - Redis: localhost:6379"

echo ""
print_status "To stop services:"
echo "  make all-down"
echo "  or"
echo "  ./scripts/stop-services.sh"