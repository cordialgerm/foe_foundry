#!/bin/bash
# Shell script wrapper for code formatting
# This provides an easy way to format code from the command line

set -e

cd "$(dirname "$0")/.."

echo "🔧 Formatting Python code with Ruff..."

# Run the Python formatting script
python scripts/format_code.py "$@"