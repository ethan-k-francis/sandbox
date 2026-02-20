# =============================================================================
# __main__.py — Module Entry Point
# =============================================================================
# Runs when executed as: python -m username_generator
# Delegates immediately to the CLI — keeps this file as a thin wrapper.
# =============================================================================

from username_generator.cli import main

if __name__ == "__main__":
    main()
