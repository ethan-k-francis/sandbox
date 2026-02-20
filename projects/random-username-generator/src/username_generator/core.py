# =============================================================================
# core.py — Username Generation Engine
# =============================================================================
# Pure business logic — no CLI, no I/O, no side effects.
#
# The generator works in 3 steps:
#   1. Pick a pattern (random weighted or explicit)
#   2. Fill placeholders with random words from wordlists
#   3. Apply casing style (PascalCase, snake_case, etc.)
#
# Dependency Inversion: cli.py calls core.py, never the reverse.
# This means the generator is reusable as a library — import it in a
# web API, Discord bot, or anywhere else without touching CLI code.
# =============================================================================

import random
import re

from username_generator.config import (
    MAX_NUMBER,
    MAX_USERNAME_LENGTH,
    MIN_NUMBER,
    PATTERN_WEIGHTS,
    PATTERNS,
    CaseStyle,
)
from username_generator.wordlists import ADJECTIVES, NOUNS, VERBS


def generate_username(
    *,
    pattern: str | None = None,
    style: CaseStyle = CaseStyle.PASCAL,
    max_length: int = MAX_USERNAME_LENGTH,
) -> str:
    """Generate a single random username.

    Args:
        pattern: Pattern name from PATTERNS dict. None = weighted random.
        style: Casing style for the output.
        max_length: Maximum character length. Retries if exceeded.

    Returns:
        A random username string.

    Raises:
        ValueError: If the pattern name doesn't exist.
    """
    if pattern and pattern not in PATTERNS:
        valid = ", ".join(sorted(PATTERNS.keys()))
        raise ValueError(f"Unknown pattern '{pattern}'. Valid patterns: {valid}")

    # Retry loop — some word combos exceed max_length, so regenerate.
    # Bounded to prevent infinite loops on impossible constraints.
    for _ in range(50):
        selected_pattern = pattern or _pick_weighted_pattern()
        template = PATTERNS[selected_pattern]
        tokens = _fill_template(template)
        username = _apply_style(tokens, style)

        if len(username) <= max_length:
            return username

    # Fallback: truncate if we can't find a short enough combo
    return username[:max_length]


def generate_batch(
    count: int,
    *,
    pattern: str | None = None,
    style: CaseStyle = CaseStyle.PASCAL,
    unique: bool = True,
    max_length: int = MAX_USERNAME_LENGTH,
) -> list[str]:
    """Generate multiple usernames at once.

    Args:
        count: Number of usernames to generate.
        pattern: Pattern name. None = weighted random (each may differ).
        style: Casing style applied to all usernames.
        unique: If True, no duplicates in the batch.
        max_length: Maximum character length per username.

    Returns:
        List of generated usernames.
    """
    if not unique:
        return [
            generate_username(pattern=pattern, style=style, max_length=max_length)
            for _ in range(count)
        ]

    # Use a set for O(1) dedup lookups instead of checking a list each time
    seen: set[str] = set()
    results: list[str] = []
    # Cap iterations to avoid infinite loop if the word space is exhausted
    max_attempts = count * 10

    for _ in range(max_attempts):
        if len(results) >= count:
            break
        username = generate_username(pattern=pattern, style=style, max_length=max_length)
        if username not in seen:
            seen.add(username)
            results.append(username)

    return results


def _pick_weighted_pattern() -> str:
    """Select a random pattern name using configured weights.

    Uses random.choices which implements weighted sampling via
    cumulative distribution — O(n) setup, O(log n) per sample.
    """
    names = list(PATTERN_WEIGHTS.keys())
    weights = list(PATTERN_WEIGHTS.values())
    return random.choices(names, weights=weights, k=1)[0]


def _fill_template(template: str) -> list[str]:
    """Replace placeholders in a pattern template with random words.

    Returns a list of tokens (words and numbers) rather than a concatenated
    string. This preserves word boundaries so _apply_style can correctly
    join them with separators (snake_case, kebab-case, etc.).

    Literal text between placeholders (like "the" in "the{adj}{noun}")
    is preserved as its own token.
    """
    tokens: list[str] = []
    remainder = template

    while remainder:
        # Find the next placeholder
        match = re.search(r"\{(adj|noun|verb|num)\}", remainder)
        if not match:
            # No more placeholders — remaining text is a literal token
            if remainder:
                tokens.append(remainder)
            break

        # Capture any literal text before the placeholder as its own token
        if match.start() > 0:
            tokens.append(remainder[: match.start()])

        # Replace the placeholder with a random word
        placeholder = match.group(1)
        if placeholder == "adj":
            tokens.append(random.choice(ADJECTIVES))
        elif placeholder == "noun":
            tokens.append(random.choice(NOUNS))
        elif placeholder == "verb":
            tokens.append(_verbify(random.choice(VERBS)))
        elif placeholder == "num":
            tokens.append(str(random.randint(MIN_NUMBER, MAX_NUMBER)))

        remainder = remainder[match.end() :]

    return tokens


def _verbify(verb: str) -> str:
    """Convert a base verb to an agent noun by adding 'er' suffix.

    Handles English spelling rules:
      - Silent 'e': gaze → gazer (not gazeer)
      - Double consonant: run → runner, spin → spinner
      - Default: jump → jumper

    Not comprehensive (English is messy) but covers the verbs in our list.
    """
    if verb.endswith("e"):
        return verb + "r"
    # Double the final consonant for short CVC (consonant-vowel-consonant) verbs
    if (
        len(verb) >= 3
        and verb[-1] not in "aeiouwy"
        and verb[-2] in "aeiou"
        and verb[-3] not in "aeiou"
    ):
        return verb + verb[-1] + "er"
    return verb + "er"


def _apply_style(tokens: list[str], style: CaseStyle) -> str:
    """Apply a casing style to a list of word/number tokens.

    Receives pre-split tokens from _fill_template, so word boundaries
    are already known — no need to guess where words start and end.
    """
    # Normalize all tokens to lowercase
    tokens = [t.lower() for t in tokens]

    match style:
        case CaseStyle.PASCAL:
            return "".join(t.capitalize() if t.isalpha() else t for t in tokens)
        case CaseStyle.LOWER:
            return "".join(tokens)
        case CaseStyle.UPPER:
            return "".join(tokens).upper()
        case CaseStyle.SNAKE:
            return "_".join(tokens)
        case CaseStyle.KEBAB:
            return "-".join(tokens)
