# =============================================================================
# core.py — Business Logic
# =============================================================================
# Contains the actual logic of the application, independent of the CLI layer.
#
# Why separate core.py from cli.py?
#   - core.py has NO knowledge of Click, command-line arguments, or terminal output.
#   - It takes plain Python types and returns plain Python types.
#   - This makes it testable: tests call build_greeting() directly without
#     simulating CLI invocations.
#   - It's reusable: if you later add a web API or GUI, they call the same
#     core functions.
#
# This is the Dependency Inversion Principle in action:
#   cli.py depends on core.py (calls its functions)
#   core.py depends on nothing (no imports from cli.py)
#   The "outer" layer (CLI) depends on the "inner" layer (logic), not vice versa.
# =============================================================================


def build_greeting(name: str, *, loud: bool = False) -> str:
    """Build a greeting string for the given name.

    Args:
        name: The person's name to greet.
        loud: If True, return the greeting in uppercase.

    Returns:
        The formatted greeting string.

    Examples:
        >>> build_greeting("Alice")
        'Hello, Alice!'
        >>> build_greeting("Bob", loud=True)
        'HELLO, BOB!'
    """
    greeting = f"Hello, {name}!"

    if loud:
        greeting = greeting.upper()

    return greeting
