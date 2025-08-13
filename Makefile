# Tahoe Application
.PHONY: help up down logs ps clean

help:
	@echo "Tahoe Platform"
	@echo "=============="
	@echo ""
	@echo "Infrastructure Services:"
	@echo "  make up     - Start infrastructure (postgres, redis)"
	@echo "  make down   - Stop infrastructure services"
	@echo "  make logs   - View logs from infrastructure"
	@echo "  make ps     - Show running infrastructure"
	@echo "  make clean  - Remove containers and volumes"
	@echo ""
	@echo "Individual Services:"
	@echo "  cd services/agent-engine && make docker-up"
	@echo "  cd services/auth && make up          (future)"
	@echo "  cd services/billing && make up       (future)"

up:
	docker-compose up -d
	@echo ""
	@echo "Infrastructure running:"
	@echo "  PostgreSQL:   localhost:5432"
	@echo "  Redis:        localhost:6379"
	@echo ""
	@echo "Start individual services:"
	@echo "  cd services/agent-engine && make docker-up"

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v