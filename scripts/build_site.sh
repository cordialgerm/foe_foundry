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

# If --fast is set, set SKIP_WHOOSH_INIT env variable
if [ "$FAST_BUILD" = true ]; then
    export SKIP_WHOOSH_INIT=1
fi

# Build the static content unless --fast is present
if [ "$FAST_BUILD" = false ]; then
    echo "Building the static site with MkDocs..."
    poetry run mkdocs build --clean
    echo "MkDocs build completed successfully."
else
    echo "Skipping MkDocs build due to --fast flag."
fi

# When FAST_BUILD is set, copy /docs/css/ and /docs/scripts/ to /site/css/ and /site/scripts/
if [ "$FAST_BUILD" = true ]; then
    echo "Copying /docs/css/ and /docs/scripts/ to /site/..."
    mkdir -p site/css site/scripts
    cp -r docs/css/. site/css/
    cp -r docs/scripts/. site/scripts/
    echo "Copy completed."
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
if [ "$FAST_BUILD" = true ]; then
    poetry run python -m foe_foundry_data --fast
else
    poetry run python -m foe_foundry_data
fi


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
    if [ "$FAST_BUILD" = true ]; then
        poetry run python -m foe_foundry_site --fast
    else
        poetry run python -m foe_foundry_site
    fi
fi