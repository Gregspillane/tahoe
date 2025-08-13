# Tahoe Application
.PHONY: help up down logs ps clean

help:
	@echo "Tahoe Application"
	@echo "================"
	@echo ""
	@echo "  make up     - Start all services (agent-engine, postgres, redis)"
	@echo "  make down   - Stop all services"
	@echo "  make logs   - View logs from all services"
	@echo "  make ps     - Show running services"
	@echo "  make clean  - Remove containers and volumes"

up:
	docker-compose up -d
	@echo ""
	@echo "Services running:"
	@echo "  Agent Engine: http://localhost:8001"
	@echo "  PostgreSQL:   localhost:5432"
	@echo "  Redis:        localhost:6379"

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v