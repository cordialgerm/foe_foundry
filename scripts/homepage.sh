#!/bin/bash

# Configuration
PORT=8080
START_PAGE="docs/test.html"

# Launch Python HTTP server
echo "Starting local server on http://localhost:$PORT..."
python3 -m http.server $PORT &

# Save the PID so we can kill it later if needed
SERVER_PID=$!

# Give the server a second to start
sleep 1

# Open in default browser
open "http://localhost:$PORT/$START_PAGE"

# Wait for user to end script manually (Ctrl+C)
trap "echo 'Stopping server...'; kill $SERVER_PID; exit" INT
wait