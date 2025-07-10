#!/bin/bash

# === CONFIGURATION ===
BASE_URL="http://127.0.0.1:8080"
PDF_OUTPUT="page.pdf"
IMG_OUTPUT="page-%03d.png"
WAIT_TIME=20
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# === INPUT VALIDATION ===
if [ -z "$1" ]; then
  echo "Usage: ./publish_page.sh /relative/path"
  exit 1
fi

RELATIVE_PATH="$1"
FULL_URL="${BASE_URL}${RELATIVE_PATH}"

# Optional: sanitize filename output based on path
SAFE_PATH=$(echo "$RELATIVE_PATH" | tr '/' '-' | sed 's/^-//')
PDF_OUTPUT="${SAFE_PATH}.pdf"
IMG_OUTPUT="${SAFE_PATH}-%03d.png"

# === START LOCAL SERVER ===
echo "Starting server..."
poetry run python -m foe_foundry_site &
SERVER_PID=$!

# === WAIT FOR SERVER TO BE READY ===
echo "Waiting $WAIT_TIME seconds for server to start..."
sleep $WAIT_TIME

# === PRINT TO PDF ===
echo "Saving $FULL_URL to $PDF_OUTPUT..."
"$CHROME_BIN" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf="$PDF_OUTPUT" \
  "$FULL_URL"

# === CONVERT TO IMAGE ===
echo "Converting $PDF_OUTPUT to image(s)..."
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r600 \
  -sOutputFile="$IMG_OUTPUT" \
  "$PDF_OUTPUT"

# === CLEANUP ===
echo "Stopping server..."
kill $SERVER_PID

echo "✅ Done! Images saved as $IMG_OUTPUT"