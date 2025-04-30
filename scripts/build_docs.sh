# build_docs.sh
#!/bin/bash

# Make sure we stop on any error
set -e

# Move to the script's directory (optional but good for robustness)
cd "$(dirname "$0")/.."

# Set PYTHONPATH and build
PYTHONPATH=. mkdocs build --clean