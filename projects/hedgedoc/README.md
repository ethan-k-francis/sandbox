# HedgeDoc

Batteries-included deployment of [HedgeDoc](https://hedgedoc.org/) — a real-time collaborative Markdown editor. One command to start, with Caddy reverse proxy, automated backups, full-text search, and a management CLI.

## Quick Start

```bash
# Clone and start (Docker is the only prerequisite)
cd projects/hedgedoc
make up
```

Open [http://localhost](http://localhost). That's it.

`make up` handles everything on first run: validates Docker is installed, generates cryptographic secrets, creates the `.env` file, and starts all services.

## What's Included

| Component | Purpose |
|-----------|---------|
| **HedgeDoc 1.10.6** | Collaborative Markdown editor with real-time sync, presentation mode, revision history |
| **PostgreSQL 17** | Database backend for notes, users, and revisions |
| **Caddy 2** | Reverse proxy with compression, security headers, automatic HTTPS for production |
| **Backup/Restore** | One-command database + uploads backup with timestamped archives |
| **Management CLI** | Full-text search, user management, note export, system status |
| **Auto-generated secrets** | Session and database secrets generated on first run, never committed |

## Architecture

```
Browser ──► Caddy (:80) ──► HedgeDoc (:3000) ──► PostgreSQL (:5432)
                                  │
                                  └──► uploads volume (images, attachments)
```

**Why these choices:**
- **Caddy over Nginx**: 15 lines of config, built-in compression, automatic TLS for production. Nginx needs 80+ lines and manual cert management.
- **PostgreSQL over SQLite**: HedgeDoc's default SQLite breaks under concurrent WebSocket writes. Postgres handles it correctly and supports `pg_dump` for clean backups.
- **Docker Compose**: Self-contained, reproducible, runs on any machine with Docker. No cloud dependencies.

## Commands

```bash
make up              # Start everything (first-run setup included)
make down            # Stop all services
make restart         # Restart all services
make logs            # Tail all service logs
make logs-app        # Tail only HedgeDoc logs
make status          # Show health, note count, DB size, upload count

make backup          # Create timestamped backup (SQL + uploads)
make restore BACKUP=backups/hedgedoc-2026-02-22-143000

make create-user EMAIL=me@example.com PASSWORD=secret
make users           # List all registered users
make search QUERY="kubernetes deployment"
make notes           # List recent notes
make export          # Export all notes as Markdown files

make shell           # Shell into the HedgeDoc container
make db-shell        # Open a psql session
make clean           # Stop and delete all data (DESTRUCTIVE)
```

## Configuration

All configuration lives in `.env` (auto-generated from `.env.example` on first run).

### Key Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `HEDGEDOC_DOMAIN` | `localhost` | Domain name (set for production) |
| `HEDGEDOC_PORT` | `80` | Port Caddy listens on |
| `CMD_ALLOW_ANONYMOUS` | `true` | Allow anonymous note creation |
| `CMD_ALLOW_FREEURL` | `true` | Create notes by visiting any URL (Etherpad-style) |
| `CMD_EMAIL` | `true` | Enable email/password registration |
| `CMD_DEFAULT_PERMISSION` | `editable` | Default permission for new notes |
| `CMD_ENABLE_STATS_API` | `true` | Enable `/status` and `/metrics` endpoints |

### Production Setup

For a public deployment, edit `.env`:

```env
HEDGEDOC_DOMAIN=notes.example.com
CMD_PROTOCOL_USESSL=true
CMD_ALLOW_ANONYMOUS=false
CMD_ALLOW_EMAIL_REGISTER=false
```

Then update the `Caddyfile` — replace `:80` with your domain:

```
notes.example.com {
    reverse_proxy app:3000
    encode zstd gzip
    # ... same headers ...
}
```

Caddy automatically provisions a Let's Encrypt TLS certificate.

### GitHub OAuth (Optional)

Uncomment in `.env` and fill in your [GitHub OAuth app](https://github.com/settings/developers) credentials:

```env
CMD_GITHUB_CLIENTID=your-client-id
CMD_GITHUB_CLIENTSECRET=your-client-secret
```

## Backup & Restore

### Creating a Backup

```bash
make backup
# Creates: backups/hedgedoc-2026-02-22-143000/
#   database.sql    — Full PostgreSQL dump
#   uploads.tar.gz  — All uploaded images/files
#   metadata.txt    — Timestamp, note count, versions
```

### Restoring a Backup

```bash
# List available backups
make restore

# Restore a specific backup (replaces all current data)
make restore BACKUP=backups/hedgedoc-2026-02-22-143000
```

### Automated Backups

Add to crontab for daily backups:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/hedgedoc && make backup
```

## Full-Text Search

Search across all notes by content and title:

```bash
make search QUERY="docker compose networking"
```

Results are ranked by relevance using PostgreSQL's built-in full-text search (`ts_rank` + `plainto_tsquery`).

## Project Structure

```
projects/hedgedoc/
├── README.md              # This file
├── Makefile               # All operations as make targets
├── docker-compose.yml     # Caddy + HedgeDoc + PostgreSQL
├── Caddyfile              # Reverse proxy configuration
├── .env.example           # Configuration template (copied to .env)
├── .gitignore             # Ignores .env, backups/, data/
├── config/
│   └── default.md         # Template for new notes
└── scripts/
    ├── setup.sh           # First-run setup (prereqs + secret generation)
    ├── backup.sh          # Database + uploads backup
    ├── restore.sh         # Restore from backup archive
    └── hedgedoc-cli.py    # Management CLI (search, users, export, status)
```

## Features

HedgeDoc includes out of the box:

- **Real-time collaboration** — Multiple users editing the same document simultaneously
- **Presentation mode** — Add `/slide` to any note URL for a reveal.js slideshow
- **Revision history** — Every edit is tracked, with diff view between versions
- **Markdown extensions** — Mermaid diagrams, MathJax equations, code highlighting, embedded videos
- **Export** — Download notes as Markdown, HTML, or PDF (via browser print)
- **Image uploads** — Drag and drop images directly into notes
- **Table of contents** — Auto-generated from headings with `[TOC]`
- **Tags** — Organize notes with `#tags` in YAML front matter

## Troubleshooting

### HedgeDoc won't start

```bash
# Check service health
make status

# Check logs for errors
make logs-app

# Verify the database is reachable
make db-shell
# Then: \conninfo
```

### Port 80 is already in use

Change the port in `.env`:

```env
HEDGEDOC_PORT=8080
```

Then `make restart`. Access at `http://localhost:8080`.

### Reset everything

```bash
make clean    # Stops services, deletes all data and volumes
make up       # Fresh start
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 17.03+
- [Docker Compose](https://docs.docker.com/compose/install/) v2
- Python 3.8+ (for the CLI tool — already on most systems)
