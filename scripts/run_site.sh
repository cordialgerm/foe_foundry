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
export PORT=8000
export SITE_URL=http://127.0.0.1:8000/

# Run the site itself
poetry run python -m foe_foundry_site