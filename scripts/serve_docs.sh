# serve_docs.sh
#!/bin/bash

# Stop on first error
set -e

# Move back to the root of the repository
cd "$(dirname "$0")/.."

# Set PYTHONPATH so that mkdocs can find the package in this repo
export PYTHONPATH=.
export SITE_URL=${SITE_URL:-http://127.0.0.1:8000/}

# Set the correct PYTHONPATH
poetry run mkdocs serve