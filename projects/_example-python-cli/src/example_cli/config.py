# =============================================================================
# config.py — Configuration Loading
# =============================================================================
# Loads configuration from environment variables, config files, and defaults.
# Centralizes all configuration so other modules don't scatter env var reads
# throughout the codebase.
#
# Configuration hierarchy (highest priority first):
#   1. Environment variables       (runtime overrides)
#   2. Config file (.env or JSON)  (project-specific settings)
#   3. Hardcoded defaults          (safe fallbacks)
#
# Why a Config dataclass instead of raw os.getenv() calls everywhere?
#   - Single source of truth: all config is defined in one place
#   - Type safety: each field has a type, caught by mypy
#   - Testable: create Config(debug=True) in tests without setting env vars
#   - Documented: each field has a comment explaining what it controls
# =============================================================================

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration loaded from environment and defaults.

    Each field corresponds to an environment variable (uppercase, prefixed).
    """

    # Enable debug output (more verbose logging)
    # Env: EXAMPLE_CLI_DEBUG=1
    debug: bool = False

    # Default greeting template — can be overridden for i18n or custom messages
    # Env: EXAMPLE_CLI_GREETING_TEMPLATE="Howdy, {name}!"
    greeting_template: str = "Hello, {name}!"

    # Maximum number of retries for network operations (if applicable)
    # Env: EXAMPLE_CLI_MAX_RETRIES=5
    max_retries: int = 3


def load_config() -> Config:
    """Load configuration from environment variables with defaults.

    Returns a Config instance with values from the environment where set,
    falling back to defaults for anything not specified.
    """
    # Parse max_retries safely — fall back to default on non-integer input
    try:
        max_retries = int(os.getenv("EXAMPLE_CLI_MAX_RETRIES", str(Config.max_retries)))
    except ValueError:
        max_retries = Config.max_retries

    return Config(
        debug=os.getenv("EXAMPLE_CLI_DEBUG", "").lower() in ("1", "true", "yes"),
        greeting_template=os.getenv("EXAMPLE_CLI_GREETING_TEMPLATE", Config.greeting_template),
        max_retries=max_retries,
    )
