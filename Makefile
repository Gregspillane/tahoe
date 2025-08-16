# Tahoe Project Management Makefile
.PHONY: help infra-up infra-down infra-logs infra-status transcribe-up transcribe-down transcribe-logs platform-up platform-down platform-logs platform-restart platform-status all-up all-down clean reset test

# Default target
help:
	@echo "Tahoe Project Management Commands:"
	@echo ""
	@echo "Infrastructure Commands:"
	@echo "  infra-up          Start infrastructure (PostgreSQL + Redis)"
	@echo "  infra-down        Stop infrastructure"
	@echo "  infra-logs        View infrastructure logs"
	@echo "  infra-status      Check infrastructure status"
	@echo ""
	@echo "Service Commands:"
	@echo "  transcribe-up     Start transcription service"
	@echo "  transcribe-down   Stop transcription service"
	@echo "  transcribe-logs   View transcription service logs"
	@echo "  platform-up       Start platform service"
	@echo "  platform-down     Stop platform service"
	@echo "  platform-logs     View platform service logs"
	@echo "  platform-restart  Restart platform service"
	@echo "  platform-status   Check platform service status"
	@echo ""
	@echo "Combined Commands:"
	@echo "  all-up            Start infrastructure + all services"
	@echo "  all-down          Stop all services"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean             Stop all and remove containers (keep volumes)"
	@echo "  reset             Stop all, remove containers and volumes (DESTROYS DATA)"
	@echo "  test              Run basic connectivity tests"

# Infrastructure commands
infra-up:
	@echo "Starting infrastructure services..."
	cd infrastructure && docker-compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	cd infrastructure && docker-compose ps

infra-down:
	@echo "Stopping infrastructure services..."
	cd infrastructure && docker-compose down

infra-logs:
	cd infrastructure && docker-compose logs -f

infra-status:
	cd infrastructure && docker-compose ps

# Transcription service commands
transcribe-up: 
	@echo "Starting transcription service..."
	@echo "Note: Infrastructure must be running first"
	cd transcribe && docker-compose up -d
	@echo "Waiting for service to be healthy..."
	@sleep 10
	cd transcribe && docker-compose ps

transcribe-down:
	@echo "Stopping transcription service..."
	cd transcribe && docker-compose down

transcribe-logs:
	cd transcribe && docker-compose logs -f

# Platform Service Commands
platform-up:
	cd platform && docker-compose up -d

platform-down:
	cd platform && docker-compose down

platform-logs:
	cd platform && docker-compose logs -f

platform-restart:
	cd platform && docker-compose restart

platform-status:
	@echo "Platform Service Status:"
	@curl -s http://localhost:9200/health || echo "Platform service not responding"

# Combined commands
all-up: infra-up platform-up transcribe-up
	@echo "All services started"

all-down: transcribe-down platform-down infra-down
	@echo "All services stopped"

# Maintenance commands
clean: transcribe-down platform-down infra-down
	@echo "Removing containers (keeping volumes)..."
	cd transcribe && docker-compose rm -f
	cd platform && docker-compose rm -f
	cd infrastructure && docker-compose rm -f
	@echo "Cleanup complete"

reset: transcribe-down platform-down
	@echo "WARNING: This will destroy all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	cd infrastructure && docker-compose down -v
	@echo "Reset complete - all data destroyed"

# Basic connectivity test
test:
	@echo "Testing infrastructure connectivity..."
	@echo "Testing PostgreSQL..."
	docker exec tahoe-postgres psql -U tahoe_user -d tahoe -c "SELECT 'PostgreSQL OK' as status;" || echo "PostgreSQL connection failed"
	@echo "Testing Redis..."
	docker exec tahoe-redis redis-cli ping || echo "Redis connection failed"
	@echo "Testing transcription service..."
	curl -s http://localhost:9100/health || echo "Transcription service not responding"
	@echo "Testing platform service..."
	curl -s http://localhost:9200/health || echo "Platform service not responding"
	@echo "Tests complete"