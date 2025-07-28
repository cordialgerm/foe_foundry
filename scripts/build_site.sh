#!/bin/bash

# Stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Make sure the venv is in sync with the lock file
poetry install --sync

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.
export SITE_URL=${SITE_URL:-http://127.0.0.1:8080/}


# Check for --profile flag
PROFILE=0
for arg in "$@"; do
  if [ "$arg" = "--profile" ]; then
    PROFILE=1
    break
  fi
done

# Build the static content, optionally with py-spy profiling
if [ "$PROFILE" -eq 1 ]; then
  if ! command -v py-spy >/dev/null 2>&1; then
    echo "py-spy is not installed. Please install it to use profiling."
    exit 1
  fi
  echo "Profiling mkdocs build with py-spy..."
  sudo -E py-spy record -o mkdocs-profile.svg -- poetry run mkdocs build --clean
  echo "Profile saved to mkdocs-profile.svg"
else
  poetry run mkdocs build --clean
fi

# Prepare the search index
poetry run python -m foe_foundry_data