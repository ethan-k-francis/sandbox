# =============================================================================
# Example Go API — Makefile
# =============================================================================
# Common commands for building, running, testing, and linting.
#
# Usage:
#   make build    Compile the server binary
#   make run      Build and run the server
#   make test     Run all tests
#   make lint     Run golangci-lint
#   make help     Show all commands
# =============================================================================

.PHONY: help build run test lint clean

# Binary output directory and name
BIN_DIR := bin
BIN_NAME := server

# Go build flags
# -ldflags="-s -w" strips debug info for smaller binary (don't use in dev)
GOFLAGS :=

.DEFAULT_GOAL := help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the server binary
	@mkdir -p $(BIN_DIR)
	go build $(GOFLAGS) -o $(BIN_DIR)/$(BIN_NAME) ./cmd/server
	@echo "Built: $(BIN_DIR)/$(BIN_NAME)"

run: build ## Build and run the server
	./$(BIN_DIR)/$(BIN_NAME)

test: ## Run all tests with verbose output
	go test -v -race ./...

test-cover: ## Run tests with coverage report
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

lint: ## Run golangci-lint
	golangci-lint run ./...

clean: ## Remove build artifacts
	rm -rf $(BIN_DIR) coverage.out coverage.html
