#!/bin/bash

# Tahoe Services Stop Script
# This script stops all services in the correct order

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

# Change to project root directory
cd "$(dirname "$0")/.."

print_status "Stopping Tahoe services..."

# Stop transcription service first
print_status "Stopping transcription service..."
cd transcribe && docker-compose down
cd ..
print_success "Transcription service stopped"

# Stop infrastructure
print_status "Stopping infrastructure services..."
cd infrastructure && docker-compose down
cd ..
print_success "Infrastructure services stopped"

print_success "All services stopped successfully!"

# Show what's still running (if anything)
remaining=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(tahoe|transcription)" || true)
if [ -n "$remaining" ]; then
    print_warning "Some containers are still running:"
    echo "$remaining"
else
    print_success "All Tahoe containers have been stopped"
fi