# Example Python CLI Tool

A reference project showing the standard structure for a Python CLI application.
Use this as a template when starting a new Python project — CLI tool, data processor,
web scraper, ML experiment, or anything else.

**This is not a real tool** — it's a documented skeleton showing where everything goes.

## Project Structure

```text
_example-python-cli/
├── README.md               # You're reading it
├── pyproject.toml          # Project metadata, dependencies, tool config
├── src/
│   └── example_cli/        # Package directory (importable as `example_cli`)
│       ├── __init__.py     # Package marker — defines version, public API
│       ├── __main__.py     # Entry point for `python -m example_cli`
│       ├── cli.py          # CLI argument parsing (click or argparse)
│       ├── core.py         # Main business logic (the "what it does")
│       ├── config.py       # Configuration loading (env vars, files, defaults)
│       └── utils.py        # Shared helper functions
├── tests/
│   ├── __init__.py         # Makes tests/ a package (needed for pytest discovery)
│   ├── conftest.py         # Shared test fixtures (reusable test setup)
│   └── test_core.py        # Tests for core.py business logic
└── docs/
    └── DESIGN.md           # Design decisions and architecture notes
```

## Key Concepts

### Why `src/` Layout?

The `src/` layout (as opposed to flat layout) prevents a subtle bug:

```text
# Flat layout (DON'T use):
my-project/
├── example_cli/       # ← Python can import this from the working directory
│   └── __init__.py    #    even without installing the package. Tests pass
├── tests/             #    locally but fail in CI. Sneaky.
└── pyproject.toml

# src/ layout (USE THIS):
my-project/
├── src/
│   └── example_cli/   # ← Python can't import this without installing.
│       └── __init__.py #    Forces you to `pip install -e .` first.
├── tests/             #    Tests behave the same locally and in CI.
└── pyproject.toml
```

### Why `pyproject.toml` Instead of `requirements.txt`?

`pyproject.toml` is the modern standard (PEP 621). It replaces three old files:

| Old Way | New Way (pyproject.toml) |
|---|---|
| `setup.py` — package build config | `[build-system]` and `[project]` sections |
| `setup.cfg` — package metadata | `[project]` section (name, version, etc.) |
| `requirements.txt` — dependencies | `[project.dependencies]` for runtime deps |
| `requirements-dev.txt` — dev deps | `[project.optional-dependencies.dev]` |

One file, one source of truth. Plus tool config (ruff, pytest, mypy) goes here too.

### Why `__main__.py`?

It makes the package runnable as a module:

```bash
python -m example_cli          # Runs __main__.py
python -m example_cli --help   # CLI help
```

This is cleaner than a standalone script and works without modifying PATH.

## How to Set Up

```bash
cd projects/_example-python-cli

# Create a virtual environment (isolates dependencies from system Python)
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install the package in editable mode with dev dependencies
# -e means "editable" — changes to source code take effect immediately
# [dev] installs the optional dev dependencies (pytest, ruff, mypy)
pip install -e ".[dev]"

# Verify it works
python -m example_cli --help

# Run tests
pytest

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/
```

## How to Adapt This Template

1. Rename `example_cli/` to your package name (use underscores: `my_tool`)
2. Update `pyproject.toml`: name, description, dependencies
3. Replace the placeholder logic in `core.py` with your actual code
4. Update `cli.py` with your actual CLI arguments
5. Write tests in `tests/` as you go
