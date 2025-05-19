# build_docs.sh
#!/bin/bash

# Make sure we stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Make sure the venv is in sync with the lock file
poetry install --sync

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.
export SITE_URL=${SITE_URL:-http://127.0.0.1:8080/}

# if the repository is shallow, fetch the rest of the history
# this is needed for the blogging plugin, which relies on git history
if git rev-parse --is-shallow-repository; then
  git fetch --unshallow
fi

# Build the static content
poetry run mkdocs build --clean

# Prepare the search index
poetry run python -m foe_foundry_data
