#!/bin/bash

# Stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Check if Git is available
command -v git >/dev/null 2>&1 || {
  echo "❌ Error: git is not installed or not in PATH." >&2
  exit 1
}

# If the repository is shallow, fetch the rest of the history
# This is needed for the blogging plugin, which relies on git history
if git rev-parse --is-shallow-repository; then
  echo "Repository is shallow. Attempting to fetch full git history..."
  echo "📈 Commit count before fetch: $(git rev-list --count HEAD)"

  if git fetch --unshallow --progress; then
    echo "✅ Successfully fetched full history."
    echo "📈 Commit count after fetch: $(git rev-list --count HEAD)"
  else
    echo "❌ git fetch --unshallow failed!" >&2
    exit 1
  fi
else
  echo "👍 Repository is already a full clone. No fetch needed."
fi

# Make sure the venv is in sync with the lock file
poetry install --sync

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.
export SITE_URL=${SITE_URL:-http://127.0.0.1:8080/}

# Build the static content
poetry run mkdocs build --clean

# Prepare the search index
poetry run python -m foe_foundry_data