# =============================================================================
# utils.py — Shared Helper Functions
# =============================================================================
# Small, reusable functions that don't belong to any specific module.
# These are the kind of functions you'd use across multiple files.
#
# Rules for utils:
#   - Each function should be pure (no side effects) when possible
#   - Each function should do one thing
#   - If a utility grows into multiple related functions, promote it to its
#     own module (e.g., utils.py → string_utils.py, file_utils.py)
#   - Don't let utils.py become a dumping ground — if it's over ~100 lines,
#     it's time to split
# =============================================================================

from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Create a directory (and parents) if it doesn't exist.

    Args:
        path: The directory path to create.

    Returns:
        The same path (for chaining).

    Example:
        >>> data_dir = ensure_directory(Path("~/.my-tool/data").expanduser())
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def truncate_string(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """Truncate a string to a maximum length, adding a suffix if truncated.

    Args:
        text: The string to truncate.
        max_length: Maximum allowed length (including suffix).
        suffix: String to append when truncated (default: "...").

    Returns:
        The original string if short enough, or truncated with suffix.

    Examples:
        >>> truncate_string("Hello", max_length=10)
        'Hello'
        >>> truncate_string("Hello, World!", max_length=10)
        'Hello, ...'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
