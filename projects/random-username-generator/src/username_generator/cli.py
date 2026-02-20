# =============================================================================
# cli.py — Command-Line Interface
# =============================================================================
# Defines the CLI using Click. Thin layer — all logic delegates to core.py.
#
# Usage:
#   username-gen                      # 1 random username (default)
#   username-gen -n 10                # 10 unique usernames
#   username-gen -p classic           # Force a specific pattern
#   username-gen -s snake_case        # Change casing style
#   username-gen -n 5 -p verber       # 5 NounVerber usernames
#   username-gen patterns             # List available patterns
# =============================================================================

import click
from rich.console import Console
from rich.table import Table

from username_generator.config import PATTERNS, CaseStyle
from username_generator.core import generate_batch, generate_username

console = Console()

# Build a list of valid style names for Click's choice validation
_STYLE_NAMES = [s.value for s in CaseStyle]
_STYLE_MAP = {s.value: s for s in CaseStyle}


@click.group(invoke_without_command=True)
@click.option("-n", "--count", default=1, show_default=True, help="Number of usernames to generate")
@click.option(
    "-p",
    "--pattern",
    type=click.Choice(sorted(PATTERNS.keys()), case_sensitive=False),
    default=None,
    help="Username pattern (omit for weighted random)",
)
@click.option(
    "-s",
    "--style",
    type=click.Choice(_STYLE_NAMES, case_sensitive=False),
    default=CaseStyle.PASCAL.value,
    show_default=True,
    help="Casing style",
)
@click.option("--max-length", default=20, show_default=True, help="Max username length")
@click.option("--allow-dupes", is_flag=True, help="Allow duplicate usernames in batch")
@click.option(
    "-i",
    "--include",
    default=None,
    help="Word or number to include in every username",
)
@click.version_option()
@click.pass_context
def main(
    ctx: click.Context,
    count: int,
    pattern: str | None,
    style: str,
    max_length: int,
    allow_dupes: bool,
    include: str | None,
) -> None:
    """Generate fun random usernames — Reddit style."""
    # If a subcommand was invoked (e.g., `patterns`), don't generate
    if ctx.invoked_subcommand is not None:
        return

    case_style = _STYLE_MAP[style]

    if count == 1:
        username = generate_username(
            pattern=pattern, style=case_style, max_length=max_length, include=include
        )
        console.print(f"[bold green]{username}[/bold green]")
    else:
        usernames = generate_batch(
            count,
            pattern=pattern,
            style=case_style,
            unique=not allow_dupes,
            max_length=max_length,
            include=include,
        )
        for name in usernames:
            console.print(f"[bold green]{name}[/bold green]")


@main.command()
def patterns() -> None:
    """List all available username patterns with examples."""
    table = Table(title="Username Patterns", show_lines=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Template", style="yellow")
    table.add_column("Example", style="green")

    for name, template in sorted(PATTERNS.items()):
        # Generate a live example for each pattern
        example = generate_username(pattern=name, style=CaseStyle.PASCAL)
        table.add_row(name, template, example)

    console.print(table)
