# =============================================================================
# test_core.py — Tests for Core Business Logic
# =============================================================================
# Tests the functions in core.py. We test the business logic directly
# (not through the CLI) so tests are fast, focused, and independent
# of the CLI framework.
#
# Test naming convention:
#   test_<function_name>_<scenario>_<expected_result>
#   e.g., test_build_greeting_with_name_returns_hello
#
# Each test should:
#   1. Arrange — set up inputs
#   2. Act — call the function
#   3. Assert — check the result
# Keep tests small — one assertion per test when possible.
# =============================================================================

from example_cli.core import build_greeting


class TestBuildGreeting:
    """Tests for the build_greeting function."""

    def test_basic_greeting(self) -> None:
        """Given a name, should return 'Hello, {name}!'."""
        result = build_greeting("Alice")
        assert result == "Hello, Alice!"

    def test_loud_greeting(self) -> None:
        """Given loud=True, should return the greeting in uppercase."""
        result = build_greeting("Bob", loud=True)
        assert result == "HELLO, BOB!"

    def test_not_loud_by_default(self) -> None:
        """Loud should be False by default (no shouting unless asked)."""
        result = build_greeting("Charlie")
        assert result == result  # Not uppercase
        assert result[0] == "H"  # Starts with capital H, not all caps

    def test_empty_name(self) -> None:
        """Should handle empty string gracefully (no crash)."""
        result = build_greeting("")
        assert result == "Hello, !"

    def test_name_with_spaces(self) -> None:
        """Should handle names with spaces (full names)."""
        result = build_greeting("Ada Lovelace")
        assert result == "Hello, Ada Lovelace!"
