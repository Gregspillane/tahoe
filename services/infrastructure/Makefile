# Infrastructure Services - PostgreSQL & Redis
.PHONY: help up down logs status clean

help:
	@echo "Infrastructure Services (PostgreSQL & Redis)"
	@echo "==========================================="
	@echo ""
	@echo "  make up      - Start infrastructure services"
	@echo "  make down    - Stop infrastructure services"
	@echo "  make logs    - View service logs"
	@echo "  make status  - Check service status"
	@echo "  make clean   - Remove volumes and data"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	docker-compose down -v