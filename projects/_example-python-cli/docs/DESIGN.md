# Design Notes — Example Python CLI

## Architecture

This project follows a layered architecture:

```text
┌─────────────────────────────┐
│         cli.py              │  ← Presentation layer (Click commands)
│   Parses args, formats      │     Knows about CLI, doesn't know business logic
│   output, handles errors    │
├─────────────────────────────┤
│         core.py             │  ← Business logic layer
│   Pure functions, no I/O,   │     Doesn't know about CLI or terminal
│   no side effects           │
├─────────────────────────────┤
│       config.py             │  ← Configuration layer
│   Loads env vars, files,    │     Provides typed config to all layers
│   defaults                  │
├─────────────────────────────┤
│       utils.py              │  ← Shared utilities
│   Pure helper functions     │     No dependencies on other project modules
└─────────────────────────────┘
```

Dependencies flow downward: cli.py imports core.py, core.py imports config.py.
Nothing imports cli.py. This makes the core testable without the CLI.

## Decisions

| Decision | Choice | Why |
|---|---|---|
| CLI framework | Click | Declarative, composable, better than argparse for multi-command CLIs |
| Terminal output | Rich | Colors, tables, progress bars — makes CLI tools feel professional |
| Linter | Ruff | Replaces flake8+isort+black in one fast tool |
| Type checker | Mypy | Catches bugs at "compile time" — worth the annotation cost |
| Test framework | Pytest | Less boilerplate than unittest, better fixtures and plugins |
| Package layout | src/ | Prevents accidental imports, matches pip install behavior |
