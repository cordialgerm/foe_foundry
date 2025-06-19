#!/bin/bash

set -euo pipefail

# Configuration
PORT=8000

# Clean up old assets
echo "Cleaning up old assets..."
rm -f ./site/css/site.*.css
rm -f ./site/css/homepage.*.css
rm -f ./site/scripts/extras.*.js
rm -f ./site/scripts/homepage.*.js

# Copy new assets
echo "Copying updated assets..."
cp ./docs/css/site.css ./site/css/site.css
cp ./docs/css/homepage.css ./site/css/homepage.css
cp ./docs/scripts/extras.js ./site/scripts/extras.js
cp ./docs/scripts/homepage.js ./site/scripts/homepage.js
cp -r ./docs/img/ ./site/img/


# Create home page
echo "Creating home page..."
if ! poetry run python -m docs_gen.homepage; then
    echo "Python script failed. Exiting."
    exit 1
fi

# Launch Python HTTP server
echo "Starting local server on http://localhost:$PORT..."
poetry run python -m http.server $PORT --directory site &

# Save the PID so we can kill it later if needed
SERVER_PID=$!

# Give the server a second to start
sleep 1

# Open in default browser
open "http://localhost:$PORT/index.html"

# Wait for user to end script manually (Ctrl+C)
trap "echo 'Stopping server...'; kill $SERVER_PID; exit" INT
wait