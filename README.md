[![CI](https://github.com/ethan-k-francis/sandbox/actions/workflows/ci.yml/badge.svg)](https://github.com/ethan-k-francis/sandbox/actions/workflows/ci.yml)
[![Security](https://github.com/ethan-k-francis/sandbox/actions/workflows/security.yml/badge.svg)](https://github.com/ethan-k-francis/sandbox/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# Sandbox

Experiments, prototypes, and learning projects. This is the place to try new languages,
libraries, patterns, and tools. Each project is self-contained — move fast, but keep things
documented so you can come back and understand what you built.

## Repository Structure

```text
sandbox/
├── projects/                      # All projects live here
│   ├── _example-python-cli/      # Reference Python project
│   ├── _example-go-api/          # Reference Go project
│   ├── your-experiment-name/     # Your actual projects
│   └── ...
├── .github/workflows/            # CI/CD pipelines
├── AGENTS.md                     # Project context for AI and humans
├── Makefile                      # Repo-level commands (make help)
├── .pre-commit-config.yaml       # Git hooks for linting
├── .gitignore                    # Ignores build artifacts, secrets, IDE files
├── .markdownlint.yaml            # Markdown linting config
└── .yamllint.yaml                # YAML linting config
```

## Quick Start

```bash
# 1. Clone and enter the repo
cd ~/repositories/sandbox

# 2. Install git hooks (linting + commit message cleanup)
make install-hooks

# 3. See all available commands
make help
```

## How to Create a New Project

Every project lives in `projects/` as its own self-contained folder. Use the example
projects as a reference for structure.

### Step 1: Create the project folder

```bash
mkdir -p projects/my-experiment
cd projects/my-experiment
```

### Step 2: Pick your language and set up the structure

See the templates below for your language. Copy what you need from the example projects
or build from scratch.

---

### Python Project Structure

Use this for CLI tools, data processing, ML experiments, web scrapers, automation scripts,
or anything Python. See `projects/_example-python-cli/` for a complete reference.

```text
my-python-project/
├── README.md               # REQUIRED: What this does, how to run, what you learned
├── pyproject.toml          # Project metadata, dependencies, tool config (ruff, pytest)
├── src/
│   └── my_project/         # Package directory (underscore, not hyphen)
│       ├── __init__.py     # Package marker + version
│       ├── __main__.py     # Entry point for `python -m my_project`
│       ├── cli.py          # CLI argument parsing (click or argparse)
│       ├── core.py         # Main business logic
│       ├── config.py       # Configuration loading (env vars, files)
│       └── utils.py        # Shared helper functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures for pytest
│   └── test_core.py        # Tests for core logic
└── docs/
    └── DESIGN.md           # Design decisions and architecture notes
```

**Key files explained:**

| File | What It Does | Why It Exists |
|---|---|---|
| `pyproject.toml` | Defines dependencies, build config, and tool settings | Single source of truth for project metadata (replaces setup.py, setup.cfg, requirements.txt) |
| `src/my_project/` | Source code in a proper package layout | `src/` layout prevents accidental imports from the working directory |
| `__main__.py` | Makes the package runnable with `python -m my_project` | Clean entry point without needing a separate script |
| `conftest.py` | Shared pytest fixtures (test data, mock clients, etc.) | DRY — reuse test setup across all test files |

**How to set up a new Python project:**

```bash
# Create the structure
mkdir -p projects/my-project/src/my_project projects/my-project/tests projects/my-project/docs

# Create a virtual environment (isolated dependencies)
cd projects/my-project
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode (after writing pyproject.toml)
pip install -e ".[dev]"

# Run it
python -m my_project

# Run tests
pytest
```

---

### Go Project Structure

Use this for CLI tools, HTTP APIs, system utilities, or concurrent programs.
See `projects/_example-go-api/` for a complete reference.

```text
my-go-project/
├── README.md               # REQUIRED: What this does, how to build, how to run
├── go.mod                  # Module path and dependencies
├── go.sum                  # Dependency checksums (auto-generated)
├── Makefile                # Build, run, test commands
├── cmd/
│   └── server/             # (or cli/, worker/, etc.) — one folder per binary
│       └── main.go         # Entry point — minimal, just wires things up
├── internal/               # Private application code (not importable by others)
│   ├── handlers/           # HTTP handlers (or CLI commands)
│   │   └── health.go
│   ├── middleware/          # HTTP middleware (logging, auth, etc.)
│   │   └── logging.go
│   ├── models/             # Data structures (structs, interfaces)
│   │   └── item.go
│   ├── service/            # Business logic (use cases, orchestration)
│   │   └── item_service.go
│   └── config/             # Configuration loading
│       └── config.go
├── pkg/                    # Public library code (importable by other projects)
│   └── ...                 # Only create if you want to share code externally
├── tests/
│   └── integration_test.go # Integration tests (unit tests go next to source files)
└── docs/
    └── DESIGN.md           # Design decisions and architecture notes
```

**Key files explained:**

| File/Dir | What It Does | Why It Exists |
|---|---|---|
| `cmd/server/main.go` | Entry point — creates dependencies and starts the app | Go convention: `cmd/<binary-name>/main.go` for each executable |
| `internal/` | Private code that only this module can import | Go enforces this — other modules literally can't import `internal/` packages |
| `internal/handlers/` | HTTP route handlers (or CLI command handlers) | Separates "how requests come in" from "what the app does" |
| `internal/service/` | Business logic, independent of HTTP/CLI | Testable without spinning up a server; follows separation of concerns |
| `pkg/` | Code you want other Go projects to import | Only create this if you're building a library; most projects don't need it |
| `go.mod` | Module path + dependency versions | Go's dependency management (like package.json or Cargo.toml) |

**How to set up a new Go project:**

```bash
# Create the structure
mkdir -p projects/my-project/cmd/server projects/my-project/internal/{handlers,middleware,models,service,config}
mkdir -p projects/my-project/tests projects/my-project/docs

# Initialize the Go module
cd projects/my-project
go mod init github.com/ethan-k-francis/sandbox/projects/my-project

# Build and run
go build -o bin/server ./cmd/server
./bin/server

# Run tests
go test ./...
```

---

### Other Languages

| Language | Build File | Project Template |
|---|---|---|
| **Rust** | `Cargo.toml` | `cargo new my-project` — generates the standard structure |
| **C++** | `CMakeLists.txt` | See game-development repo `_example-metroidvania/` for CMake setup |
| **C#** | `*.csproj` | `dotnet new console -n MyProject` — generates the standard structure |
| **TypeScript** | `package.json` + `tsconfig.json` | `npm init -y && npx tsc --init` |

The patterns are the same regardless of language:

- `src/` (or language equivalent) for source code
- `tests/` for tests
- `docs/` for design notes
- `README.md` in every project
- One build/config file at the root (`pyproject.toml`, `go.mod`, `Cargo.toml`, etc.)

## Conventions

### Naming

- **Project folders:** lowercase with hyphens (`ray-tracer`, `tcp-chat-server`)
- **Prefix with `_example-`** for reference/template projects (sorts first)
- **Python packages:** `snake_case` inside `src/` (`src/my_package/`)
- **Go packages:** short lowercase names (`handlers`, `models`, `config`)

### Code Quality

- **Every file gets comments.** Someone learning should understand what it does and why.
- **Every directory gets a README.** No exceptions.
- **Performance matters.** Pick the right data structures from the start.

### Git Workflow

- Feature branches: `efrancis/feature/descriptive-name`
- PRs for all changes (never push to main directly)
- Git hooks auto-clean commit messages and run linters (installed via `make install-hooks`)

## Repo-Level Commands

```bash
make help              # Show all commands
make lint              # Run all linters
make lint-fix          # Auto-fix lint issues
make clean             # Remove generated files
make git-status        # Branch status and sync info
make git-clean-branches  # Delete merged branches
```
