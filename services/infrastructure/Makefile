# Infrastructure Services - PostgreSQL & Redis
.PHONY: help up down logs status clean db-migrate db-generate db-push db-studio

help:
	@echo "Infrastructure Services (PostgreSQL & Redis)"
	@echo "==========================================="
	@echo ""
	@echo "  make up         - Start infrastructure services"
	@echo "  make down       - Stop infrastructure services"
	@echo "  make logs       - View service logs"
	@echo "  make status     - Check service status"
	@echo "  make clean      - Remove volumes and data"
	@echo ""
	@echo "Database Operations:"
	@echo "  make db-migrate - Create and apply migrations"
	@echo "  make db-generate - Generate Prisma client"
	@echo "  make db-push    - Push schema changes (dev only)"
	@echo "  make db-studio  - Open Prisma Studio"

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

db-migrate:
	cd prisma && prisma migrate dev --name init

db-generate:
	cd prisma && prisma generate

db-push:
	cd prisma && prisma db push

db-studio:
	cd prisma && prisma studio