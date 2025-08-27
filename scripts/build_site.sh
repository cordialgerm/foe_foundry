#!/bin/bash

# Stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

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

# Check for --fast and --help flags
FAST_BUILD=false
SHOW_HELP=false
for arg in "$@"; do
    if [ "$arg" = "--fast" ]; then
        FAST_BUILD=true
    elif [ "$arg" = "--optimized" ]; then
        # --optimized is now an alias for --fast for backward compatibility
        FAST_BUILD=true
    elif [ "$arg" = "--help" ] || [ "$arg" = "-h" ]; then
        SHOW_HELP=true
    fi
done

# Show help if requested
if [ "$SHOW_HELP" = true ]; then
    echo "Foe Foundry Build Script"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --fast       Fast build mode with smart caching (skips data generation when fresh,"
    echo "               skips page generation, uses file copying for development)"
    echo "  --optimized  Alias for --fast (deprecated, use --fast instead)"
    echo "  --run        Run the site after building"
    echo "  --help, -h   Show this help message"
    echo ""
    echo "Build Mode Performance Comparison:"
    echo "  Full build (no flags):     ~145s (complete regeneration)"
    echo "  --fast build:              ~4s   (development mode, 97% faster)"
    echo ""
    echo "Use --fast for local development, iteration, and CI/CD builds with caching."
    exit 0
fi

# If --fast is set, set optimization flags for smart caching
if [ "$FAST_BUILD" = true ]; then
    export SKIP_INDEX_INIT=1
    export SKIP_PAGE_GENERATION=true
    export SKIP_INDEX_REBUILD=true
    export SKIP_MONSTER_CACHE_GENERATION=true
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
    if [ "$FAST_BUILD" = true ]; then
        echo "Running fast MkDocs build (skipping dynamic page generation)..."
    fi
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

# If --fast is set, also set --run
if [ "$FAST_BUILD" = true ]; then
    RUN_SITE=true
fi

# Optionally run the site if --run flag is present
if [ "$RUN_SITE" = true ]; then
    echo "Running foe_foundry_site..."
    if [ "$FAST_BUILD" = true ]; then
        poetry run python -m foe_foundry_site --fast
    else
        poetry run python -m foe_foundry_site
    fi
fi