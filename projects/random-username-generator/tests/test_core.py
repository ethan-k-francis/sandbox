# =============================================================================
# test_core.py — Tests for Username Generation Engine
# =============================================================================
# Tests the core logic directly — no CLI simulation needed because
# core.py is decoupled from the CLI layer (Dependency Inversion).
#
# Run: pytest (from the project root)
# =============================================================================

import re

import pytest

from username_generator.config import PATTERNS, CaseStyle
from username_generator.core import (
    _apply_style,
    _verbify,
    generate_batch,
    generate_username,
)


class TestGenerateUsername:
    """Tests for single username generation."""

    def test_returns_string(self) -> None:
        """Basic smoke test — should always return a non-empty string."""
        result = generate_username()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_respects_max_length(self) -> None:
        """Generated usernames should never exceed max_length."""
        for _ in range(100):
            result = generate_username(max_length=15)
            assert len(result) <= 15

    def test_default_style_is_pascal(self) -> None:
        """Default output should be PascalCase — first letter of each word capitalized."""
        for _ in range(20):
            result = generate_username()
            # PascalCase starts with uppercase and has no separators
            assert result[0].isupper() or result[0].isdigit()
            assert "_" not in result
            assert "-" not in result

    @pytest.mark.parametrize("pattern_name", list(PATTERNS.keys()))
    def test_all_patterns_produce_output(self, pattern_name: str) -> None:
        """Every registered pattern should produce a valid username."""
        result = generate_username(pattern=pattern_name)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_invalid_pattern_raises(self) -> None:
        """Requesting a non-existent pattern should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown pattern"):
            generate_username(pattern="nonexistent")


class TestGenerateBatch:
    """Tests for batch username generation."""

    def test_correct_count(self) -> None:
        """Batch should return exactly the requested number of usernames."""
        results = generate_batch(5)
        assert len(results) == 5

    def test_unique_by_default(self) -> None:
        """Batch usernames should be unique when unique=True (default)."""
        results = generate_batch(20)
        assert len(results) == len(set(results))

    def test_allows_dupes(self) -> None:
        """With unique=False, duplicates are allowed (but not guaranteed)."""
        # Just verify it doesn't crash — duplicates are probabilistic
        results = generate_batch(5, unique=False)
        assert len(results) == 5

    def test_empty_batch(self) -> None:
        """Requesting 0 usernames should return an empty list."""
        results = generate_batch(0)
        assert results == []


class TestCaseStyles:
    """Tests for casing style application."""

    def test_snake_case(self) -> None:
        """snake_case should use underscores and be all lowercase."""
        result = generate_username(style=CaseStyle.SNAKE)
        assert result == result.lower()
        assert "_" in result

    def test_kebab_case(self) -> None:
        """kebab-case should use hyphens and be all lowercase."""
        result = generate_username(style=CaseStyle.KEBAB)
        assert result == result.lower()
        assert "-" in result

    def test_uppercase(self) -> None:
        """UPPERCASE should be all caps with no separators."""
        result = generate_username(style=CaseStyle.UPPER)
        # Numbers don't have case — strip them for the alpha check
        alpha_only = re.sub(r"\d", "", result)
        assert alpha_only == alpha_only.upper()

    def test_lowercase(self) -> None:
        """lowercase should be all lowercase with no separators."""
        result = generate_username(style=CaseStyle.LOWER)
        assert result == result.lower()
        assert "_" not in result
        assert "-" not in result


class TestVerbify:
    """Tests for the verb → agent noun transformation."""

    def test_silent_e(self) -> None:
        """Verbs ending in 'e' should just add 'r': gaze → gazer."""
        assert _verbify("gaze") == "gazer"
        assert _verbify("blaze") == "blazer"

    def test_cvc_doubling(self) -> None:
        """Short CVC verbs double the consonant: run → runner."""
        assert _verbify("run") == "runner"
        assert _verbify("spin") == "spinner"

    def test_regular(self) -> None:
        """Regular verbs just add 'er': jump → jumper."""
        assert _verbify("jump") == "jumper"
        assert _verbify("build") == "builder"


class TestInclude:
    """Tests for the --include feature (custom word/number injection)."""

    def test_include_word_appears_in_output(self) -> None:
        """A custom word should appear somewhere in the generated username."""
        for _ in range(20):
            result = generate_username(include="phoenix")
            assert "phoenix" in result.lower()

    def test_include_number_appears_in_output(self) -> None:
        """A custom number should appear in the generated username."""
        for _ in range(20):
            result = generate_username(include="42")
            assert "42" in result

    def test_include_word_with_pattern(self) -> None:
        """Include should work with an explicit pattern."""
        result = generate_username(pattern="classic", include="dragon")
        assert "dragon" in result.lower()

    def test_include_number_forces_num_pattern(self) -> None:
        """A numeric include without explicit pattern should pick a {num} pattern."""
        for _ in range(20):
            result = generate_username(include="99")
            assert "99" in result

    def test_include_in_batch(self) -> None:
        """Include should apply to every username in a batch."""
        results = generate_batch(5, include="wolf")
        for name in results:
            assert "wolf" in name.lower()

    def test_include_with_styles(self) -> None:
        """Include should work across all casing styles."""
        result_snake = generate_username(include="ninja", style=CaseStyle.SNAKE)
        assert "ninja" in result_snake
        result_kebab = generate_username(include="ninja", style=CaseStyle.KEBAB)
        assert "ninja" in result_kebab


class TestApplyStyle:
    """Tests for the internal style application function."""

    def test_pascal_case(self) -> None:
        assert _apply_style(["brave", "falcon", "42"], CaseStyle.PASCAL) == "BraveFalcon42"

    def test_snake_case(self) -> None:
        assert _apply_style(["brave", "falcon", "42"], CaseStyle.SNAKE) == "brave_falcon_42"

    def test_kebab_case(self) -> None:
        assert _apply_style(["brave", "falcon", "42"], CaseStyle.KEBAB) == "brave-falcon-42"
