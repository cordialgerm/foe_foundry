# serve_docs.sh
#!/bin/bash

# Stop on first error
set -e

# Move to the script's directory (optional but good for robustness)
cd "$(dirname "$0")/.."

# Set the correct PYTHONPATH
PYTHONPATH=. mkdocs serve