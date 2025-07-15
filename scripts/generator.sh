#!/bin/bash

set -euo pipefail

# Configuration
PORT=8000

# Compile TypeScript files
echo "Compiling TypeScript files in src/components..."
tsconfig="tsconfig.json"
if [ -f "$tsconfig" ]; then
  npx tsc --project "$tsconfig" --noEmit
  echo "TypeScript compilation completed successfully."
else
  echo "Error: tsconfig.json not found in the project root. Aborting."
  exit 1
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

# Launch Python HTTP server
echo "Starting local server on http://localhost:$PORT..."
poetry run python -m http.server $PORT --directory site &

# Save the PID so we can kill it later if needed
SERVER_PID=$!

# Open in default browser
open "http://localhost:$PORT/index.html"

# Wait for user to end script manually (Ctrl+C)
trap "echo 'Stopping server...'; kill $SERVER_PID; exit" INT
wait