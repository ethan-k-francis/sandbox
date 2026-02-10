# =============================================================================
# conftest.py — Shared Test Fixtures
# =============================================================================
# pytest automatically discovers conftest.py and makes its fixtures available
# to all test files in the same directory (and subdirectories).
#
# Fixtures are reusable test setup — think of them as "given this scenario,
# run the test." They replace repetitive setup code in each test function.
#
# How fixtures work:
#   1. Define a function decorated with @pytest.fixture
#   2. Use it as a parameter in any test function — pytest injects it
#   3. The fixture runs before the test and (optionally) cleans up after
#
# Example:
#   @pytest.fixture
#   def sample_config():
#       return Config(debug=True)
#
#   def test_something(sample_config):    # ← pytest passes sample_config
#       assert sample_config.debug is True
# =============================================================================

import pytest

from example_cli.config import Config


@pytest.fixture
def default_config() -> Config:
    """Provide a default Config instance for tests.

    Tests that need specific config values should create their own Config
    instead of modifying this one (keeps tests independent).
    """
    return Config()


@pytest.fixture
def debug_config() -> Config:
    """Provide a Config with debug mode enabled."""
    return Config(debug=True)
