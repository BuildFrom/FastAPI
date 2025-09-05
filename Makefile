clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# ==============================================================================
# Define dependencies
# ==============================================================================
YOUR_APP       := your-api
BASE_IMAGE_NAME := docker-username
# VERSION         := 0.1.1
VERSION         := $(shell poetry version -s)
API_IMAGE       := $(BASE_IMAGE_NAME)/$(YOUR_APP):$(VERSION)

# ==============================================================================
# General Commands
# ==============================================================================

init:
	poetry new $(YOUR_APP)

track-tree:
	poetry show --tree

track-latest:
	poetry show --latest

install:
	poetry add $(cat requirements.txt)

update:
	poetry update package

dev-install:
	poetry add --dev ruff


run:
	lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs -r kill -9
	poetry run python3 app/main.py


# Use this when package is removed
lock:
	poetry lock

ruff: ## Run ruff check (use 'make lint-fix' to auto-fix)
	poetry run ruff check .

# ==============================================================================
# Versioning
# ==============================================================================

version:
	@if [ -z "$(SEMVER)" ]; then \
		poetry version; \
	else \
		poetry version $(SEMVER); \
	fi

version-help:
	@echo "Usage: make version SEMVER=<bump_type>"
	@echo ""
	@echo "Available bump types:"
	@echo "  show         Show current version"
	@echo "  patch        Bump patch version (0.0.X)"
	@echo "  minor        Bump minor version (0.X.0)"
	@echo "  major        Bump major version (X.0.0)"
	@echo "  preminor     Bump preminor version (0.X.0a0)"
	@echo "  premajor     Bump premajor version (X.0.0a0)"
	@echo "  prerelease   Bump prerelease version (0.0.0aX)"

print-version:
	@echo $(VERSION)

# make version SEMVER=x.x.x

# ==============================================================================
# Development Commands
# ==============================================================================

migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"
	poetry run alembic upgrade head

migrate-generate: ## Generate a new migration file
	@if [ -z "$(msg)" ]; then \
		echo "Usage: make migrate-generate msg='your migration message'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate-up: ## Run database migrations
	poetry run alembic upgrade head

migrate-down: ## Rollback last migration
	poetry run alembic downgrade -1

migrate-status: ## Show migration status
	poetry run alembic current

migrate-history: ## Show migration history
	poetry run alembic history

migrate-reset: ## Reset database (WARNING: This will delete all data!)
	@echo "WARNING: This will delete all data in the database!"
	@read -p "Are you sure? (y/N): " confirm && [ "$confirm" = "y" ] || exit 1
	poetry run alembic downgrade base
	poetry run alembic upgrade head

prettier: lint-fix format

lint-fix: ## Run linting with auto-fix
	poetry run ruff check --fix .

format: ## Format code
	poetry run ruff format .