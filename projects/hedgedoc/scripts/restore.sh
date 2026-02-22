#!/usr/bin/env bash
# =============================================================================
# Restore — Restores a HedgeDoc backup from a backup directory
#
# Usage:
#   ./scripts/restore.sh backups/hedgedoc-2026-02-22-143000
#
# What it does:
#   1. Validates the backup directory exists and contains required files
#   2. Stops the HedgeDoc app (database stays running)
#   3. Drops and recreates the database to ensure a clean restore
#   4. Loads the SQL dump
#   5. Restores uploaded files into the Docker volume
#   6. Restarts everything
#
# WARNING: This is destructive — it replaces the current database and uploads
# with the backup contents. Make a fresh backup first if you're unsure.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# -- Validate arguments -------------------------------------------------------

BACKUP_DIR="${1:-}"
if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: $0 <backup-directory>"
    echo ""
    echo "Available backups:"
    # shellcheck disable=SC2012
    ls -1d backups/hedgedoc-* 2>/dev/null | sort -r | head -10 || echo "  (none found)"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup directory not found: $BACKUP_DIR" >&2
    exit 1
fi

if [ ! -f "$BACKUP_DIR/database.sql" ]; then
    echo "ERROR: database.sql not found in $BACKUP_DIR" >&2
    exit 1
fi

# Load environment
if [ ! -f .env ]; then
    echo "ERROR: .env not found. Run 'make up' first." >&2
    exit 1
fi
# shellcheck disable=SC1091
source .env

echo "Restoring from: $BACKUP_DIR"
if [ -f "$BACKUP_DIR/metadata.txt" ]; then
    echo ""
    cat "$BACKUP_DIR/metadata.txt"
    echo ""
fi

# Confirm with user
read -r -p "This will REPLACE all current data. Continue? [y/N] " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# -- Stop the app (keep database running) ------------------------------------
echo "Stopping HedgeDoc app..."
docker compose stop app caddy

# -- Restore database ---------------------------------------------------------
echo "Restoring database..."

# Drop and recreate for a clean slate
docker compose exec -T database psql -U "${POSTGRES_USER}" -d postgres -c \
    "DROP DATABASE IF EXISTS ${POSTGRES_DB};"
docker compose exec -T database psql -U "${POSTGRES_USER}" -d postgres -c \
    "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};"

# Load the dump
docker compose exec -T database psql \
    -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
    < "$BACKUP_DIR/database.sql"

echo "  Database restored"

# -- Restore uploads ----------------------------------------------------------
if [ -f "$BACKUP_DIR/uploads.tar.gz" ]; then
    echo "Restoring uploads..."
    docker compose exec -T app sh -c "rm -rf /hedgedoc/public/uploads/*" 2>/dev/null || true
    docker compose cp "$BACKUP_DIR/uploads.tar.gz" app:/tmp/uploads.tar.gz
    docker compose exec -T app tar xzf /tmp/uploads.tar.gz -C /hedgedoc/public
    docker compose exec -T app rm /tmp/uploads.tar.gz
    echo "  Uploads restored"
else
    echo "  No uploads archive found — skipping"
fi

# -- Restart everything -------------------------------------------------------
echo "Restarting services..."
docker compose up -d

echo ""
echo "Restore complete. HedgeDoc is starting up — check 'make status' in a moment."
