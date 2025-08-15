# Tahoe Project Management Makefile
.PHONY: help infra-up infra-down infra-logs infra-status transcribe-up transcribe-down transcribe-logs all-up all-down clean reset test

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
	@echo ""
	@echo "Combined Commands:"
	@echo "  all-up            Start infrastructure + transcription service"
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

# Combined commands
all-up: infra-up
	@echo "Infrastructure is up, starting transcription service..."
	@sleep 5
	$(MAKE) transcribe-up

all-down: transcribe-down infra-down
	@echo "All services stopped"

# Maintenance commands
clean: transcribe-down infra-down
	@echo "Removing containers (keeping volumes)..."
	cd transcribe && docker-compose rm -f
	cd infrastructure && docker-compose rm -f
	@echo "Cleanup complete"

reset: transcribe-down
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
	@echo "Tests complete"