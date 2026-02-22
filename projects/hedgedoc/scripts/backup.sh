#!/usr/bin/env bash
# =============================================================================
# Backup — Creates a timestamped archive of the database and uploaded files
#
# What it creates:
#   backups/hedgedoc-YYYY-MM-DD-HHMMSS/
#     database.sql     — Full PostgreSQL dump (pg_dump, plain SQL format)
#     uploads.tar.gz   — Compressed archive of all uploaded images/files
#     metadata.txt     — Backup timestamp, versions, and note count
#
# The database dump uses pg_dump's plain format (not custom) so it can be
# inspected and restored with standard psql — no special tools needed.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Load environment for DB credentials
if [ ! -f .env ]; then
    echo "ERROR: .env not found. Run 'make up' first." >&2
    exit 1
fi
# shellcheck disable=SC1091
source .env

TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
BACKUP_DIR="backups/hedgedoc-${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_DIR"

# -- Database dump ------------------------------------------------------------
echo "  Dumping database..."
docker compose exec -T database pg_dump \
    -U "${POSTGRES_USER}" \
    "${POSTGRES_DB}" \
    > "${BACKUP_DIR}/database.sql"

DB_SIZE=$(wc -c < "${BACKUP_DIR}/database.sql")
echo "  Database dump: $(numfmt --to=iec "$DB_SIZE" 2>/dev/null || echo "${DB_SIZE} bytes")"

# -- Uploaded files -----------------------------------------------------------
echo "  Archiving uploads..."

# Copy uploads from the Docker volume to a temp dir, then tar it.
# This avoids needing to know the volume mount path on the host.
UPLOAD_COUNT=$(docker compose exec -T app find /hedgedoc/public/uploads -type f 2>/dev/null | wc -l || echo "0")

if [ "$UPLOAD_COUNT" -gt 0 ]; then
    docker compose exec -T app tar czf - -C /hedgedoc/public uploads \
        > "${BACKUP_DIR}/uploads.tar.gz"
    UPLOAD_SIZE=$(wc -c < "${BACKUP_DIR}/uploads.tar.gz")
    echo "  Uploads archive: $(numfmt --to=iec "$UPLOAD_SIZE" 2>/dev/null || echo "${UPLOAD_SIZE} bytes") (${UPLOAD_COUNT} files)"
else
    echo "  No uploads found — skipping"
fi

# -- Metadata -----------------------------------------------------------------
NOTE_COUNT=$(docker compose exec -T database psql \
    -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -t -c \
    "SELECT COUNT(*) FROM \"Notes\";" 2>/dev/null | tr -d ' ' || echo "unknown")

cat > "${BACKUP_DIR}/metadata.txt" <<EOF
HedgeDoc Backup
===============
Timestamp:    ${TIMESTAMP}
Notes:        ${NOTE_COUNT}
Database:     ${DB_SIZE} bytes
Uploads:      ${UPLOAD_COUNT} files
HedgeDoc:     1.10.6
PostgreSQL:   17-alpine
EOF

echo ""
echo "Backup complete: ${BACKUP_DIR}"
echo "  Notes: ${NOTE_COUNT} | DB: $(numfmt --to=iec "$DB_SIZE" 2>/dev/null || echo "${DB_SIZE}B") | Uploads: ${UPLOAD_COUNT} files"
