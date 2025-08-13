# Agent Engine Service
.PHONY: help install dev run test validate clean

help:
	@echo "Agent Engine Service"
	@echo "==================="
	@echo ""
	@echo "  make install  - Install Python dependencies"
	@echo "  make dev      - Run development server (port 8001)"
	@echo "  make run      - Run production server"
	@echo "  make test     - Run tests"
	@echo "  make validate - Validate ADK patterns"
	@echo "  make clean    - Clean cache files"
	@echo ""
	@echo "Note: Start infrastructure first:"
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