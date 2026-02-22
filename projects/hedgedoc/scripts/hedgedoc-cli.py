#!/usr/bin/env python3
"""
HedgeDoc CLI — Management tool for the HedgeDoc Docker stack.

Provides convenience commands for common operations that would otherwise
require remembering Docker exec commands and SQL queries.

Commands:
    status      Show service health, note count, DB size, upload count
    search      Full-text search across all notes
    users       List all registered users
    create-user Create a new user account (email + password)
    export      Export all notes as individual Markdown files
    notes       List recent notes with titles and timestamps

Usage:
    python3 scripts/hedgedoc-cli.py status
    python3 scripts/hedgedoc-cli.py search "kubernetes deployment"
    python3 scripts/hedgedoc-cli.py users
    python3 scripts/hedgedoc-cli.py create-user user@example.com mypassword
    python3 scripts/hedgedoc-cli.py export ./exported-notes/
    python3 scripts/hedgedoc-cli.py notes --limit 20
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Project root is one level up from the scripts/ directory
PROJECT_DIR = Path(__file__).resolve().parent.parent


def run_psql(query: str, json_output: bool = False) -> str:
    """Execute a SQL query against the HedgeDoc database via docker compose exec.

    Uses psql inside the running database container so we don't need
    a local PostgreSQL client or network access to the container.
    """
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "database",
        "psql",
        "-U",
        os.environ.get("POSTGRES_USER", "hedgedoc"),
        "-d",
        os.environ.get("POSTGRES_DB", "hedgedoc"),
        "-t",  # Tuples only (no headers/footers)
    ]
    if json_output:
        cmd.extend(["-A"])  # Unaligned output for cleaner parsing

    cmd.extend(["-c", query])

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Database query failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def run_docker_compose(args: list[str]) -> str:
    """Run a docker compose command and return stdout."""
    result = subprocess.run(
        ["docker", "compose", *args],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def load_env() -> None:
    """Load .env file into os.environ for DB credential access."""
    env_file = PROJECT_DIR / ".env"
    if not env_file.exists():
        print("ERROR: .env not found. Run 'make up' first.", file=sys.stderr)
        sys.exit(1)
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


# -- Commands -----------------------------------------------------------------


def cmd_status(_args: argparse.Namespace) -> None:
    """Show service health, note count, database size, and upload stats."""
    print("HedgeDoc Status")
    print("=" * 50)

    # Service health via docker compose ps
    print("\nServices:")
    ps_output = run_docker_compose(
        ["ps", "--format", "table {{.Name}}\t{{.Status}}\t{{.Ports}}"]
    )
    if ps_output:
        for line in ps_output.splitlines():
            print(f"  {line}")
    else:
        print("  No services running")

    # Database stats
    print("\nDatabase:")
    note_count = run_psql('SELECT COUNT(*) FROM "Notes";')
    user_count = run_psql('SELECT COUNT(*) FROM "Users";')
    db_size = run_psql(
        f"SELECT pg_size_pretty(pg_database_size('{os.environ.get('POSTGRES_DB', 'hedgedoc')}'));"
    )
    print(f"  Notes: {note_count.strip()}")
    print(f"  Users: {user_count.strip()}")
    print(f"  Size:  {db_size.strip()}")

    # Upload stats
    print("\nUploads:")
    upload_info = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "app",
            "sh",
            "-c",
            "find /hedgedoc/public/uploads -type f | wc -l",
        ],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
    )
    upload_count = (
        upload_info.stdout.strip() if upload_info.returncode == 0 else "unknown"
    )
    print(f"  Files: {upload_count}")


def cmd_search(args: argparse.Namespace) -> None:
    """Full-text search across all note content and titles."""
    query = args.query
    limit = args.limit

    # PostgreSQL full-text search with ts_rank for relevance ordering.
    # This searches both the title and the raw markdown content.
    sql = f"""
        SELECT
            "shortid",
            COALESCE("title", '(untitled)') AS title,
            LEFT("content", 120) AS preview,
            "updatedAt"
        FROM "Notes"
        WHERE
            to_tsvector('english', COALESCE("title", '') || ' ' || COALESCE("content", ''))
            @@ plainto_tsquery('english', '{query}')
        ORDER BY
            ts_rank(
                to_tsvector('english', COALESCE("title", '') || ' ' || COALESCE("content", '')),
                plainto_tsquery('english', '{query}')
            ) DESC
        LIMIT {limit};
    """
    results = run_psql(sql)

    if not results:
        print(f"No notes matching '{query}'")
        return

    print(f"Search results for '{query}':")
    print("-" * 60)
    for line in results.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            short_id, title, preview, updated = parts[0], parts[1], parts[2], parts[3]
            preview_clean = preview.replace("\n", " ").strip()
            print(f"\n  [{short_id}] {title}")
            print(f"    Updated: {updated}")
            print(f"    Preview: {preview_clean}...")


def cmd_users(_args: argparse.Namespace) -> None:
    """List all registered users."""
    sql = """
        SELECT
            "id",
            COALESCE("email", '(no email)') AS email,
            COALESCE("profile"::json->>'name', '(no name)') AS name,
            "createdAt"
        FROM "Users"
        ORDER BY "createdAt" DESC;
    """
    results = run_psql(sql)

    if not results:
        print("No registered users")
        return

    print(f"{'ID':<6} {'Email':<30} {'Name':<20} {'Created'}")
    print("-" * 80)
    for line in results.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4:
            uid, email, name, created = parts[0], parts[1], parts[2], parts[3]
            print(f"{uid:<6} {email:<30} {name:<20} {created}")


def cmd_create_user(args: argparse.Namespace) -> None:
    """Create a new user via the HedgeDoc CLI inside the container."""
    email = args.email
    password = args.password

    # HedgeDoc provides a bin/manage_users script for user management.
    # Running it inside the container with NODE_ENV=production.
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "-e",
            "NODE_ENV=production",
            "app",
            "node",
            "bin/manage_users",
            "--add",
            email,
            "--pass",
            password,
        ],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"User created: {email}")
    else:
        print(f"Failed to create user: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def cmd_notes(args: argparse.Namespace) -> None:
    """List recent notes with titles and timestamps."""
    limit = args.limit
    sql = f"""
        SELECT
            "shortid",
            COALESCE("title", '(untitled)') AS title,
            LENGTH("content") AS chars,
            "updatedAt",
            "createdAt"
        FROM "Notes"
        ORDER BY "updatedAt" DESC
        LIMIT {limit};
    """
    results = run_psql(sql)

    if not results:
        print("No notes found")
        return

    print(f"{'ID':<12} {'Title':<40} {'Chars':<8} {'Updated'}")
    print("-" * 90)
    for line in results.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            short_id, title, chars, updated, _created = (
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
            )
            title_truncated = title[:38] + ".." if len(title) > 40 else title
            print(f"{short_id:<12} {title_truncated:<40} {chars:<8} {updated}")


def cmd_export(args: argparse.Namespace) -> None:
    """Export all notes as individual Markdown files."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sql = """
        SELECT "shortid", COALESCE("title", 'untitled'), "content"
        FROM "Notes"
        ORDER BY "updatedAt" DESC;
    """
    results = run_psql(sql)

    if not results:
        print("No notes to export")
        return

    count = 0
    for line in results.splitlines():
        parts = line.split("|", 2)
        if len(parts) >= 3:
            short_id = parts[0].strip()
            title = parts[1].strip()
            content = parts[2].strip()

            # Sanitize the title for use as a filename
            safe_title = "".join(c if c.isalnum() or c in "-_ " else "" for c in title)
            safe_title = safe_title.strip().replace(" ", "-")[:60] or "untitled"
            filename = f"{safe_title}-{short_id}.md"

            filepath = output_dir / filename
            filepath.write_text(content + "\n")
            count += 1

    print(f"Exported {count} notes to {output_dir}/")


# -- CLI parser ---------------------------------------------------------------


def main() -> None:
    """Parse arguments and dispatch to the appropriate command."""
    load_env()

    parser = argparse.ArgumentParser(
        description="HedgeDoc management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    subparsers.add_parser("status", help="Show service health and stats")

    # search
    search_parser = subparsers.add_parser(
        "search", help="Full-text search across notes"
    )
    search_parser.add_argument("query", help="Search terms")
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Max results (default: 10)"
    )

    # users
    subparsers.add_parser("users", help="List all registered users")

    # create-user
    create_parser = subparsers.add_parser(
        "create-user", help="Create a new user account"
    )
    create_parser.add_argument("email", help="User email address")
    create_parser.add_argument("password", help="User password")

    # notes
    notes_parser = subparsers.add_parser("notes", help="List recent notes")
    notes_parser.add_argument(
        "--limit", type=int, default=10, help="Max results (default: 10)"
    )

    # export
    export_parser = subparsers.add_parser(
        "export", help="Export all notes as Markdown files"
    )
    export_parser.add_argument("output_dir", help="Directory to export notes into")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "status": cmd_status,
        "search": cmd_search,
        "users": cmd_users,
        "create-user": cmd_create_user,
        "notes": cmd_notes,
        "export": cmd_export,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
