.PHONY: help install dev test lint format clean migrations migrate docker-up docker-down docker-logs db-init

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

install-dev: ## Install dependencies including dev packages
	poetry install --with dev

dev: ## Run development server with hot reload
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests with coverage
	poetry run pytest -v --cov=app --cov-report=term-missing --cov-report=html

test-unit: ## Run unit tests only
	poetry run pytest tests/unit -v

test-integration: ## Run integration tests only
	poetry run pytest tests/integration -v

test-e2e: ## Run end-to-end tests only
	poetry run pytest tests/e2e -v

lint: ## Run linters (black, isort, flake8, mypy)
	poetry run black --check app tests
	poetry run isort --check app tests
	poetry run flake8 app tests
	poetry run mypy app

format: ## Format code with black and isort
	poetry run black app tests
	poetry run isort app tests

clean: ## Clean up cache and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build

migrations: ## Generate new migration (usage: make migrations message="your message")
	poetry run alembic revision --autogenerate -m "$(message)"

migrate: ## Run database migrations
	poetry run alembic upgrade head

migrate-down: ## Rollback last migration
	poetry run alembic downgrade -1

migrate-history: ## Show migration history
	poetry run alembic history

db-init: ## Initialize database with initial data
	poetry run python scripts/init_db.py

db-reset: ## Reset database (drop and recreate)
	poetry run alembic downgrade base
	poetry run alembic upgrade head
	poetry run python scripts/init_db.py

superuser: ## Create a superuser (interactive)
	poetry run python scripts/create_superuser.py

seed: ## Seed database with test data
	poetry run python scripts/seed_data.py

docker-build: ## Build Docker images
	docker-compose -f docker/docker-compose.yml build

docker-up: ## Start all Docker services
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop all Docker services
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## Show Docker logs
	docker-compose -f docker/docker-compose.yml logs -f

docker-ps: ## Show running Docker containers
	docker-compose -f docker/docker-compose.yml ps

docker-shell: ## Open shell in app container
	docker-compose -f docker/docker-compose.yml exec app /bin/bash

docker-clean: ## Clean up Docker volumes and images
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f

docker-rebuild: ## Rebuild and restart Docker services
	docker-compose -f docker/docker-compose.yml down
	docker-compose -f docker/docker-compose.yml build --no-cache
	docker-compose -f docker/docker-compose.yml up -d

celery-worker: ## Start Celery worker
	poetry run celery -A app.tasks.celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	poetry run celery -A app.tasks.celery_app beat --loglevel=info

celery-flower: ## Start Flower (Celery monitoring)
	poetry run celery -A app.tasks.celery_app flower --port=5555

pre-commit-install: ## Install pre-commit hooks
	poetry run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

poetry-update: ## Update Poetry dependencies
	poetry update

poetry-lock: ## Update Poetry lock file
	poetry lock --no-update

poetry-export: ## Export requirements.txt
	poetry export -f requirements.txt --output requirements.txt --without-hashes

check: lint test ## Run linters and tests

all: install migrate dev ## Install, migrate, and run development server
