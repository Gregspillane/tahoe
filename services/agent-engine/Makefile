# Agent Engine Service
.PHONY: help install dev run test validate clean docker-up docker-down docker-logs

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

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands - includes all services for development
docker-up:
	docker-compose up -d
	@echo "Services starting..."
	@sleep 3
	@docker-compose ps
	@echo ""
	@echo "Agent Engine: http://localhost:8001"
	@echo "PostgreSQL:   localhost:5432"
	@echo "Redis:        localhost:6379"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f