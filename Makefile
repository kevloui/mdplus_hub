.PHONY: dev dev-backend dev-frontend build up down logs test test-backend test-frontend lint format clean

dev:
	docker-compose up --build

dev-backend:
	docker-compose up backend worker db redis

dev-frontend:
	docker-compose up frontend

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test: test-backend test-frontend

test-backend:
	docker-compose exec backend pytest -v

test-frontend:
	docker-compose exec frontend pnpm test

lint:
	docker-compose exec backend ruff check src tests
	docker-compose exec frontend pnpm lint

format:
	docker-compose exec backend ruff format src tests
	docker-compose exec frontend pnpm format

clean:
	docker-compose down -v --rmi local
	rm -rf backend/.pytest_cache
	rm -rf frontend/.next
	rm -rf frontend/node_modules

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(name)"

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh
