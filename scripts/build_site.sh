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
export PORT=${PORT:-8080}


# Check for --fast flag
FAST_BUILD=false
for arg in "$@"; do
    if [ "$arg" = "--fast" ]; then
        FAST_BUILD=true
    fi
done

# Build the static content unless --fast is present
if [ "$FAST_BUILD" = false ]; then
    echo "Building the static site with MkDocs..."
    poetry run mkdocs build --clean
    echo "MkDocs build completed successfully."
else
    echo "Skipping MkDocs build due to --fast flag."
fi

# Build the project using Vite
echo "Building the project with Vite..."
if command -v npx vite &> /dev/null; then
    npx vite build
    echo "Vite build completed successfully."
else
    echo "Error: Vite is not installed. Aborting."
    exit 1
fi

# Prepare the search index
poetry run python -m foe_foundry_data


# Check for --run flag
RUN_SITE=false
for arg in "$@"; do
    if [ "$arg" = "--run" ]; then
        RUN_SITE=true
    fi
done

# Optionally run the site if --run flag is present
if [ "$RUN_SITE" = true ]; then
    echo "Running foe_foundry_site..."
    poetry run python -m foe_foundry_site
fi