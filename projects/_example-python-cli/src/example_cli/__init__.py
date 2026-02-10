# =============================================================================
# example_cli — Package Initialization
# =============================================================================
# This file makes the directory a Python package (importable with `import example_cli`).
#
# What belongs here:
#   - Package version (single source of truth — pyproject.toml reads this)
#   - Public API exports (so users can do `from example_cli import SomeClass`)
#   - Nothing else — keep it minimal
#
# What does NOT belong here:
#   - Heavy imports or initialization (slows down every import)
#   - Business logic (goes in core.py or other modules)
# =============================================================================

__version__ = "0.1.0"
