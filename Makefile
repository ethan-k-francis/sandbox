# =============================================================================
# Sandbox - Makefile
# =============================================================================
# Common commands for development and maintenance.
#
# Usage:
#   make help        Show all available commands
#   make lint        Run all linters
# =============================================================================

.PHONY: help setup-hooks lint lint-fix lint-update lint-yaml lint-markdown lint-python \
       test clean update-deps git-clean-branches git-status

# Default target
.DEFAULT_GOAL := help

# Colors
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# =============================================================================
# Help
# =============================================================================
help: ## Show this help
	@echo ""
	@echo "$(CYAN)Sandbox - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# Setup
# =============================================================================
setup-hooks: ## Configure local git hooks (strips IDE trailers from commits)
	@git config core.hooksPath .githooks
	@echo "$(GREEN)Git hooks configured (.githooks/)$(NC)"

# =============================================================================
# Linting & Validation
# =============================================================================
lint: ## Run all linters (pre-commit hooks)
	@echo "$(CYAN)Running all linters...$(NC)"
	@pre-commit run --all-files || (echo "$(YELLOW)Some checks failed. Run 'make lint-fix' to auto-fix.$(NC)" && exit 1)
	@echo "$(GREEN)All checks passed!$(NC)"

lint-fix: ## Run linters with auto-fix enabled
	@echo "$(CYAN)Running linters with auto-fix...$(NC)"
	@pre-commit run --all-files || true
	@echo "$(GREEN)Auto-fix complete. Review changes and commit.$(NC)"

lint-update: ## Update pre-commit hooks to latest versions
	@pre-commit autoupdate
	@echo "$(GREEN)Hooks updated. Run 'make lint' to test.$(NC)"

lint-yaml: ## Lint YAML files only
	@echo "$(CYAN)Linting YAML...$(NC)"
	@yamllint -c .yamllint.yaml . 2>/dev/null || \
		echo "$(YELLOW)Install: pip install yamllint$(NC)"

lint-markdown: ## Lint Markdown files only
	@echo "$(CYAN)Linting Markdown...$(NC)"
	@markdownlint --config .markdownlint.yaml "**/*.md" 2>/dev/null || \
		echo "$(YELLOW)Install: npm install -g markdownlint-cli$(NC)"

lint-python: ## Lint Python files only
	@echo "$(CYAN)Linting Python...$(NC)"
	@ruff check . 2>/dev/null || echo "$(YELLOW)Install: pip install ruff$(NC)"
	@ruff format --check . 2>/dev/null || true

# =============================================================================
# Development
# =============================================================================
test: ## Run smoke tests (config validation)
	@echo "$(CYAN)Running smoke tests...$(NC)"
	@PASS=0; FAIL=0; \
	echo ""; \
	echo "--- Config Files ---"; \
	for f in .pre-commit-config.yaml .gitignore AGENTS.md; do \
		if [ -f "$$f" ]; then \
			echo "  $(GREEN)✓$(NC) $$f exists"; \
			PASS=$$((PASS+1)); \
		else \
			echo "  $(YELLOW)✗$(NC) $$f missing"; \
			FAIL=$$((FAIL+1)); \
		fi; \
	done; \
	echo ""; \
	echo "$(CYAN)Results: $$PASS passed, $$FAIL failed$(NC)"

# =============================================================================
# Operations & Maintenance
# =============================================================================
update-deps: ## Update pre-commit hooks and show outdated pip packages
	@echo "$(CYAN)Updating pre-commit hooks...$(NC)"
	@pre-commit autoupdate
	@echo ""
	@echo "$(CYAN)Outdated pip packages:$(NC)"
	@pip list --outdated 2>/dev/null || echo "  pip not available"
	@echo "$(GREEN)Done. Review changes and commit.$(NC)"

# =============================================================================
# Git Maintenance
# =============================================================================
git-clean-branches: ## Delete merged feature branches (local and remote)
	@echo "$(CYAN)Finding merged branches...$(NC)"
	@git fetch --prune
	@MERGED=$$(git branch --merged main | grep -v '^\*\|main$$' | sed 's/^ *//'); \
	if [ -z "$$MERGED" ]; then \
		echo "$(GREEN)No merged branches to clean up$(NC)"; \
	else \
		echo ""; \
		echo "Merged branches to delete:"; \
		echo "$$MERGED" | while read -r branch; do echo "  - $$branch"; done; \
		echo ""; \
		read -p "Delete these branches locally and remotely? (y/n): " confirm; \
		if [ "$$confirm" = "y" ]; then \
			echo "$$MERGED" | while read -r branch; do \
				git branch -d "$$branch" 2>/dev/null && echo "  $(GREEN)✓$(NC) Deleted local: $$branch"; \
				git push origin --delete "$$branch" 2>/dev/null && echo "  $(GREEN)✓$(NC) Deleted remote: $$branch"; \
			done; \
			echo "$(GREEN)Branch cleanup complete$(NC)"; \
		else \
			echo "Cancelled."; \
		fi; \
	fi

git-status: ## Show branch status and sync info
	@echo "$(CYAN)Branch: $$(git branch --show-current)$(NC)"
	@echo ""
	@git status --short
	@echo ""
	@echo "$(CYAN)Local branches:$(NC)"
	@git branch -vv
	@echo ""
	@echo "$(CYAN)Remote drift:$(NC)"
	@git fetch --dry-run 2>&1 || echo "  Up to date"

# =============================================================================
# Cleanup
# =============================================================================
clean: ## Clean generated files
	@echo "$(CYAN)Cleaning generated files...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
	@echo "$(GREEN)Cleaned generated files$(NC)"
