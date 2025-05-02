# run_site.sh
#!/bin/bash

# Make sure we stop on any error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Make sure the venv is in sync with the lock file
poetry install --sync

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.

export HOST=${HOST:-127.0.0.1}
export PORT=${PORT:-8000}
export SITE_URL=${SITE_URL:-http://$HOST:$PORT/}

# Run the site itself
echo "Starting Foe Foundry site at $SITE_URL"
poetry run uvicorn --host=$HOST --port=$PORT --proxy-headers foe_foundry_site.app:app