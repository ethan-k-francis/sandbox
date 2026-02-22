# =============================================================================
# HedgeDoc — Makefile
# One-command operations for the entire HedgeDoc stack.
#
# Quick start:   make up        (does everything — setup, secrets, start)
# Stop:          make down
# Backup:        make backup
# Search notes:  make search QUERY="my search terms"
# =============================================================================

.DEFAULT_GOAL := help

# -- Lifecycle ----------------------------------------------------------------

.PHONY: up
up: setup ## Start all services (runs first-time setup if needed)
	docker compose up -d
	@echo ""
	@echo "HedgeDoc is starting up..."
	@echo "  Open http://localhost:$$(grep -s '^HEDGEDOC_PORT' .env | cut -d= -f2 || echo 80)"
	@echo "  Run 'make status' to check health"
	@echo "  Run 'make logs' to follow logs"

.PHONY: down
down: ## Stop all services
	docker compose down

.PHONY: restart
restart: ## Restart all services
	docker compose restart

.PHONY: setup
setup: ## Run first-time setup (idempotent — safe to run multiple times)
	@bash scripts/setup.sh

# -- Observability ------------------------------------------------------------

.PHONY: logs
logs: ## Tail logs from all services
	docker compose logs -f

.PHONY: logs-app
logs-app: ## Tail only HedgeDoc application logs
	docker compose logs -f app

.PHONY: status
status: ## Show service health, note count, DB size
	@python3 scripts/hedgedoc-cli.py status

# -- Data Management ----------------------------------------------------------

.PHONY: backup
backup: ## Create a timestamped backup (database + uploads)
	@bash scripts/backup.sh

.PHONY: restore
restore: ## Restore from a backup: make restore BACKUP=backups/hedgedoc-2026-...
	@if [ -z "$(BACKUP)" ]; then \
		echo "Usage: make restore BACKUP=backups/hedgedoc-YYYY-MM-DD-HHMMSS"; \
		echo ""; \
		echo "Available backups:"; \
		ls -1d backups/hedgedoc-* 2>/dev/null | sort -r | head -10 || echo "  (none)"; \
		exit 1; \
	fi
	@bash scripts/restore.sh "$(BACKUP)"

# -- User Management ----------------------------------------------------------

.PHONY: create-user
create-user: ## Create a user: make create-user EMAIL=x@y.com PASSWORD=secret
	@if [ -z "$(EMAIL)" ] || [ -z "$(PASSWORD)" ]; then \
		echo "Usage: make create-user EMAIL=user@example.com PASSWORD=mypassword"; \
		exit 1; \
	fi
	@python3 scripts/hedgedoc-cli.py create-user "$(EMAIL)" "$(PASSWORD)"

.PHONY: users
users: ## List all registered users
	@python3 scripts/hedgedoc-cli.py users

# -- Note Operations ----------------------------------------------------------

.PHONY: search
search: ## Full-text search: make search QUERY="search terms"
	@if [ -z "$(QUERY)" ]; then \
		echo "Usage: make search QUERY=\"search terms\""; \
		exit 1; \
	fi
	@python3 scripts/hedgedoc-cli.py search "$(QUERY)"

.PHONY: notes
notes: ## List recent notes
	@python3 scripts/hedgedoc-cli.py notes

.PHONY: export
export: ## Export all notes as Markdown: make export DIR=./exported-notes
	@python3 scripts/hedgedoc-cli.py export "$(or $(DIR),./exported-notes)"

# -- Debug / Shell Access -----------------------------------------------------

.PHONY: shell
shell: ## Open a shell in the HedgeDoc container
	docker compose exec app sh

.PHONY: db-shell
db-shell: ## Open a psql session to the database
	docker compose exec database psql -U $$(grep -s '^POSTGRES_USER' .env | cut -d= -f2 || echo hedgedoc)

# -- Cleanup ------------------------------------------------------------------

.PHONY: clean
clean: down ## Stop services and remove all data (DESTRUCTIVE)
	@echo "This will delete all notes, users, and uploads."
	@read -r -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 0
	docker compose down -v
	rm -rf data/ backups/
	@echo "All data removed. Run 'make up' to start fresh."

# -- Help ---------------------------------------------------------------------

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
