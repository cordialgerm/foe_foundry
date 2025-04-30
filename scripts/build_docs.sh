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

# Build the site
poetry run mkdocs build --clean