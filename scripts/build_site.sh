#!/bin/bash

# Stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Ensure Poetry uses the correct Python version if available
if command -v python3.13 &> /dev/null; then
    poetry env use python3.13
elif command -v python3.12 &> /dev/null; then
    poetry env use python3.12
elif command -v python3.11 &> /dev/null; then
    poetry env use python3.11
fi

# Make sure the venv is in sync with the lock file
poetry install --sync

# Make sure the node modules are in sync with the lock file
npm ci

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.
export SITE_URL=${SITE_URL:-http://127.0.0.1:8080/}
export PORT=${PORT:-8080}

# Set NODE_ENV to 'development' if not already specified
export NODE_ENV=${NODE_ENV:-development}
echo "NODE_ENV is set to: $NODE_ENV"

# Check for --fast flag
FAST_BUILD=false
for arg in "$@"; do
    if [ "$arg" = "--fast" ]; then
        FAST_BUILD=true
    fi
done

# If --fast is set, set SKIP_INDEX_INIT env variable
if [ "$FAST_BUILD" = true ]; then
    export SKIP_INDEX_INIT=1
fi

# Prepare the cached content
if [ "$FAST_BUILD" = false ]; then
    rm -rf cache/
    echo "Preparing indexes..."
    poetry run python -m foe_foundry_data
    poetry run python -m foe_foundry_search
else
    echo "Skipping cache preparation due to --fast flag."
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

    # Handle uniquified extras.js filename
    if [ -f "docs/scripts/extras.js" ]; then
        # Look for existing extras.*.js files in site/scripts/
        EXTRAS_FILE=$(find site/scripts/ -name "extras.*.js" -type f | head -1)

        if [ -n "$EXTRAS_FILE" ]; then
            echo "Found uniquified extras file: $EXTRAS_FILE"
            echo "Copying docs/scripts/extras.js to match uniquified name..."
            cp docs/scripts/extras.js "$EXTRAS_FILE"
        fi
    fi

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