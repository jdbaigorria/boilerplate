.PHONY: help install dev test lint format clean migrations migrate docker-up docker-down docker-logs db-init

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv pip install -e .

install-dev: ## Install dependencies including dev packages
	uv pip install -e ".[dev]"

sync: ## Sync dependencies with uv (creates uv.lock)
	uv sync

dev: ## Run development server with hot reload
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests with coverage
	uv run pytest -v --cov=app --cov-report=term-missing --cov-report=html

test-unit: ## Run unit tests only
	uv run pytest tests/unit -v

test-integration: ## Run integration tests only
	uv run pytest tests/integration -v

test-e2e: ## Run end-to-end tests only
	uv run pytest tests/e2e -v

lint: ## Run linters (ruff, black, isort, mypy)
	uv run ruff check app tests
	uv run black --check app tests
	uv run isort --check app tests
	uv run mypy app

format: ## Format code with black and isort
	uv run black app tests
	uv run isort app tests
	uv run ruff check --fix app tests

clean: ## Clean up cache and build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build

migrations: ## Generate new migration (usage: make migrations message="your message")
	uv run alembic revision --autogenerate -m "$(message)"

migrate: ## Run database migrations
	uv run alembic upgrade head

migrate-down: ## Rollback last migration
	uv run alembic downgrade -1

migrate-history: ## Show migration history
	uv run alembic history

db-init: ## Initialize database with initial data
	uv run python scripts/init_db.py

db-reset: ## Reset database (drop and recreate)
	uv run alembic downgrade base
	uv run alembic upgrade head
	uv run python scripts/init_db.py

superuser: ## Create a superuser (interactive)
	uv run python scripts/create_superuser.py

seed: ## Seed database with test data
	uv run python scripts/seed_data.py

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
	uv run celery -A app.tasks.celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	uv run celery -A app.tasks.celery_app beat --loglevel=info

celery-flower: ## Start Flower (Celery monitoring)
	uv run celery -A app.tasks.celery_app flower --port=5555

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

uv-lock: ## Update uv.lock file
	uv lock

uv-update: ## Update dependencies
	uv lock --upgrade

check: lint test ## Run linters and tests

all: install-dev migrate dev ## Install, migrate, and run development server
