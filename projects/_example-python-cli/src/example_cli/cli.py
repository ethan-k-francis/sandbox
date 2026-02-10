# =============================================================================
# cli.py — Command-Line Interface
# =============================================================================
# Defines the CLI commands, arguments, and options using Click.
#
# Click vs argparse:
#   argparse is built-in but verbose and clunky for complex CLIs.
#   Click is declarative (decorators), composable (groups of commands),
#   and handles types, validation, and help text automatically.
#
# CLI structure:
#   example-cli --help             Show help
#   example-cli greet NAME         Greet someone
#   example-cli greet NAME --loud  Greet loudly (uppercase)
#
# How Click works:
#   @click.command() turns a function into a CLI command.
#   @click.argument("name") adds a required positional argument.
#   @click.option("--loud") adds an optional flag.
#   Click automatically generates --help from docstrings and decorators.
# =============================================================================

import click
from rich.console import Console

from example_cli.config import load_config
from example_cli.core import build_greeting

# Rich console for pretty terminal output (colors, formatting)
console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """Example CLI tool — template for Python projects.

    This is the top-level command group. Subcommands are defined below.
    """


@main.command()
@click.argument("name")
@click.option("--loud", is_flag=True, help="SHOUT the greeting")
@click.option("--count", default=1, help="Number of times to greet")
def greet(name: str, loud: bool, count: int) -> None:
    """Greet someone by name.

    NAME is the person to greet (required).
    """
    # Load configuration (env vars → defaults) and build the greeting
    config = load_config()
    greeting = build_greeting(name, loud=loud, template=config.greeting_template)

    # Print the greeting the requested number of times
    for _ in range(count):
        console.print(f"[bold green]{greeting}[/bold green]")


@main.command()
def info() -> None:
    """Show project information."""
    from example_cli import __version__

    console.print(f"[bold]example-cli[/bold] v{__version__}")
    console.print("A template CLI project for learning Python packaging.")
