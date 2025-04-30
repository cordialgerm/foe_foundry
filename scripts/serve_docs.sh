# serve_docs.sh
#!/bin/bash

# Stop on first error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Make sure the venv is in sync with the lock file
poetry install --sync

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.

# Set the correct PYTHONPATH
poetry run mkdocs serve