# =============================================================================
# Makefile — Job Aggregator
# =============================================================================
# Common commands for development, testing, and database management.
# Run `make help` to see all available targets.
# =============================================================================

.DEFAULT_GOAL := help
.PHONY: help dev dev-deps db-up db-down db-reset migrate migrate-create \
        test test-cov lint lint-fix typecheck clean

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
NC     := \033[0m

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
help: ## Show this help message
	@echo "$(CYAN)Job Aggregator — Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
dev: ## Start the FastAPI dev server with auto-reload
	@echo "$(CYAN)Starting dev server...$(NC)"
	python -m job_aggregator

dev-deps: ## Install project + dev dependencies in editable mode
	@echo "$(CYAN)Installing dependencies...$(NC)"
	pip install -e ".[dev]"

# ---------------------------------------------------------------------------
# Docker (PostgreSQL + Redis)
# ---------------------------------------------------------------------------
db-up: ## Start PostgreSQL and Redis containers
	@echo "$(CYAN)Starting database services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services ready. PostgreSQL: localhost:5432, Redis: localhost:6379$(NC)"

db-down: ## Stop database containers (keeps data)
	docker compose down

db-reset: ## Stop containers AND delete all data volumes
	@echo "$(YELLOW)Warning: This deletes all data!$(NC)"
	docker compose down -v

# ---------------------------------------------------------------------------
# Database migrations (Alembic)
# ---------------------------------------------------------------------------
migrate: ## Run all pending database migrations
	@echo "$(CYAN)Running migrations...$(NC)"
	alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	@echo "$(CYAN)Creating migration...$(NC)"
	alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback the last migration
	alembic downgrade -1

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------
test: ## Run tests
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=job_aggregator --cov-report=term-missing

# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------
lint: ## Run linter checks
	ruff check src/ tests/
	ruff format --check src/ tests/

lint-fix: ## Auto-fix lint issues
	ruff check --fix src/ tests/
	ruff format src/ tests/

typecheck: ## Run mypy type checker
	mypy src/

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
clean: ## Remove generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned.$(NC)"
