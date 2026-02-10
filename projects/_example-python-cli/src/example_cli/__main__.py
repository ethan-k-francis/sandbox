# =============================================================================
# __main__.py — Module Entry Point
# =============================================================================
# This file runs when you execute: python -m example_cli
#
# It simply calls the CLI entry point. This is the standard way to make a
# Python package runnable as a module. The actual CLI logic lives in cli.py.
#
# Why separate __main__.py from cli.py?
#   - __main__.py is a thin wrapper — just calls main()
#   - cli.py defines the CLI interface (arguments, options, help text)
#   - This lets cli.py be imported by tests without triggering execution
# =============================================================================

from example_cli.cli import main

# Only runs when executed as a module (python -m example_cli)
# Does NOT run when imported (import example_cli)
if __name__ == "__main__":
    main()
