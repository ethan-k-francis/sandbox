#!/bin/bash
# Strip Co-authored-by trailers added by IDE extensions
# This hook is run by pre-commit during prepare-commit-msg stage
# Usage: strip-ide-trailers.sh COMMIT_MSG_FILE

COMMIT_MSG_FILE="$1"

# Validate input
if [ -z "$COMMIT_MSG_FILE" ]; then
    echo "Error: No commit message file provided" >&2
    exit 1
fi

if [ ! -f "$COMMIT_MSG_FILE" ]; then
    echo "Error: Commit message file does not exist: $COMMIT_MSG_FILE" >&2
    exit 1
fi

if [ ! -r "$COMMIT_MSG_FILE" ]; then
    echo "Error: Commit message file is not readable: $COMMIT_MSG_FILE" >&2
    exit 1
fi

# Strip Cursor Co-authored-by lines
# Using sed with backup file for cross-platform compatibility (macOS/Linux)
sed -i.bak '/^Co-authored-by: Cursor/d' "$COMMIT_MSG_FILE" && rm -f "$COMMIT_MSG_FILE.bak"

exit 0
