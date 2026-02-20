# Random Username Generator

Generate fun, random usernames like Reddit does — `BraveFalcon42`, `CosmicWolfRunner`, `TheSilentPhoenix`.

## Quick Start

```bash
cd projects/random-username-generator

# Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Generate a username
username-gen

# Generate 10 usernames
username-gen -n 10
```

## Usage

```bash
# Single random username (default: PascalCase, weighted random pattern)
username-gen

# Batch generation
username-gen -n 10

# Specific pattern
username-gen -p classic        # AdjectiveNounNumber  → BraveFalcon42
username-gen -p agent          # AdjectiveNoun        → SilentWolf
username-gen -p duo            # AdjectiveAdjectiveNoun → QuietBoldTiger
username-gen -p verber         # NounVerber           → StarGazer
username-gen -p numbered_verber  # NounVerberNumber   → MoonWalker99
username-gen -p the            # TheAdjectiveNoun     → TheSwiftFox

# Casing styles
username-gen -s PascalCase     # BraveFalcon42 (default)
username-gen -s lowercase      # bravefalcon42
username-gen -s UPPERCASE      # BRAVEFALCON42
username-gen -s snake_case     # brave_falcon_42
username-gen -s kebab-case     # brave-falcon-42

# Combine options
username-gen -n 5 -p verber -s snake_case

# Max length constraint
username-gen --max-length 12

# Allow duplicates in batch
username-gen -n 100 --allow-dupes

# List all patterns with live examples
username-gen patterns

# Also works as a Python module
python -m username_generator
```

## Use as a Library

```python
from username_generator import generate_username, generate_batch
from username_generator.config import CaseStyle

# Single username
name = generate_username()

# With options
name = generate_username(pattern="verber", style=CaseStyle.SNAKE)

# Batch
names = generate_batch(10, unique=True)
```

## Project Structure

```text
random-username-generator/
├── README.md
├── pyproject.toml              # Dependencies, CLI entry point, tool config
├── src/username_generator/
│   ├── __init__.py             # Public API exports
│   ├── __main__.py             # python -m entry point
│   ├── cli.py                  # Click CLI (thin layer over core)
│   ├── config.py               # Patterns, styles, constraints
│   ├── core.py                 # Generation engine (pure logic, no I/O)
│   └── wordlists.py            # Curated adjectives, nouns, verbs
└── tests/
    └── test_core.py            # Unit tests for generation engine
```

## How It Works

1. **Pick a pattern** — weighted random or explicit (e.g., `{adj}{noun}{num}`)
2. **Fill placeholders** — replace `{adj}`, `{noun}`, `{verb}`, `{num}` with random words
3. **Apply casing** — transform tokens into the requested style (PascalCase, snake_case, etc.)

Word lists are curated for fun, memorable, SFW usernames (~140 adjectives, ~140 nouns, ~80 verbs).

## Tests

```bash
pytest              # Run all tests
pytest -v           # Verbose output
pytest --cov        # With coverage
```
