# Agent Engine Service
.PHONY: help install dev run test validate clean docker-up docker-down docker-logs dev-ui dev-ui-setup dev-ui-validate dev-ui-docker

help:
	@echo "Agent Engine Service"
	@echo "==================="
	@echo ""
	@echo "Local Python Development:"
	@echo "  make install  - Install Python dependencies"
	@echo "  make dev      - Run development server (port 8001)"
	@echo "  make run      - Run production server"
	@echo "  make test     - Run tests"
	@echo "  make validate - Validate ADK patterns"
	@echo "  make clean    - Clean cache files"
	@echo ""
	@echo "ADK Dev UI (Visual Agent Development):"
	@echo "  make dev-ui          - Launch ADK Dev UI (port 8002)"
	@echo "  make dev-ui-setup    - Install ADK and validate setup"
	@echo "  make dev-ui-validate - Validate Dev UI setup"
	@echo "  make dev-ui-docker   - Launch Dev UI in Docker"
	@echo "  NOTE: Run from agent-engine service directory: cd services/agent-engine"
	@echo ""
	@echo "Docker Development (includes Redis & PostgreSQL):"
	@echo "  make docker-up   - Start all services in Docker"
	@echo "  make docker-down - Stop all Docker services"
	@echo "  make docker-logs - View Docker logs"
	@echo ""
	@echo "Or use infrastructure separately:"
	@echo "  cd ../infrastructure && make up"

install:
	pip install -r requirements.txt

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8001

test:
	python -m pytest tests/ -v

validate:
	python scripts/validate_adk_patterns.py

clean-python:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands - includes all services for development
docker-up:
	docker-compose --env-file ../../.env up -d
	@echo "Services starting..."
	@sleep 3
	@docker-compose --env-file ../../.env ps
	@echo ""
	@echo "Agent Engine: http://localhost:8001"
	@echo "PostgreSQL:   localhost:5432"
	@echo "Redis:        localhost:6379"

docker-down:
	docker-compose --env-file ../../.env down

docker-logs:
	docker-compose --env-file ../../.env logs -f

clean:
	docker-compose --env-file ../../.env down -v

# ADK Dev UI targets
dev-ui-setup:
	@echo "Setting up ADK Dev UI..."
	@echo "Checking if google-adk is installed..."
	@pip show google-adk > /dev/null 2>&1 || (echo "Installing google-adk..." && pip install google-adk)
	@echo "Validating setup..."
	@python3 scripts/launch_dev_ui.py --validate

dev-ui-validate:
	@echo "Validating ADK Dev UI setup..."
	@python3 scripts/launch_dev_ui.py --validate

dev-ui:
	@echo "Launching Tahoe ADK Dev UI..."
	@echo "This will open a browser interface for visual agent development"
	@echo "Available at: http://localhost:8002"
	@echo ""
	@python3 scripts/launch_dev_ui.py

dev-ui-docker:
	@echo "Launching ADK Dev UI in Docker..."
	@echo "Building and starting Dev UI container..."
	@docker-compose --env-file ../../.env -f docker-compose.yml -f docker-compose.dev-ui.yml up -d dev-ui
	@echo ""
	@echo "Dev UI available at: http://localhost:8002"
	@echo "Use 'make docker-logs' to view logs"