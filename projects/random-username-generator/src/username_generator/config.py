# =============================================================================
# config.py — Username Generation Configuration
# =============================================================================
# Defines the available username patterns and casing styles.
#
# Patterns use placeholders that the generator replaces with random words:
#   {adj}  → random adjective      (e.g., "brave")
#   {noun} → random noun           (e.g., "falcon")
#   {verb} → random verb + "er"    (e.g., "gazer")
#   {num}  → random 1-4 digit number
#
# Using an enum for styles enforces valid values at the type level —
# no stringly-typed bugs from passing "Camelcase" instead of "CamelCase".
# =============================================================================

from enum import Enum


class CaseStyle(Enum):
    """How to capitalize the final username."""

    PASCAL = "PascalCase"  # BraveFalcon42 (Reddit-style default)
    LOWER = "lowercase"  # bravefalcon42
    UPPER = "UPPERCASE"  # BRAVEFALCON42
    SNAKE = "snake_case"  # brave_falcon_42
    KEBAB = "kebab-case"  # brave-falcon-42


# Each pattern is a tuple of (name, template_string, description).
# The generator picks a random pattern (or a specific one by name).
# Weighted toward patterns that produce the best-sounding usernames.
PATTERNS: dict[str, str] = {
    "classic": "{adj}{noun}{num}",  # BraveFalcon42 — the Reddit standard
    "duo": "{adj}{adj}{noun}",  # QuietBoldTiger — double adjective
    "agent": "{adj}{noun}",  # SilentWolf — clean, no number
    "verber": "{noun}{verb}",  # StarGazer — noun + action
    "numbered_verber": "{noun}{verb}{num}",  # MoonWalker99
    "the": "the{adj}{noun}",  # TheSwiftFox — definite article
}

# Default pattern weights for random selection — higher weight = more likely.
# "classic" is weighted highest because it's the most recognizable style.
PATTERN_WEIGHTS: dict[str, int] = {
    "classic": 40,
    "agent": 20,
    "duo": 15,
    "verber": 15,
    "numbered_verber": 5,
    "the": 5,
}

# Constraints
MAX_USERNAME_LENGTH = 20
MAX_NUMBER = 9999
MIN_NUMBER = 0
