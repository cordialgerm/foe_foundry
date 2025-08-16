#!/usr/bin/env bash
set -euo pipefail
set -x

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <monster_key> [base_url]" >&2
  exit 2
fi

MONSTER_KEY="$1"
BASE_URL="${2:-https://foefoundry.com}"
DEVICE_NAME="${DEVICE_NAME:-iPhone 15 Pro}"
PREROLL_SEC="${PREROLL_SEC:-2}"
DURATION_SEC="${DURATION_SEC:-15}"
OUT_DIR="${OUT_DIR:-./cache/record-monster}"
FFMPEG_FLAGS="${FFMPEG_FLAGS:--movflags +faststart -preset veryfast -crf 23 -pix_fmt yuv420p}"

RAW_DIR="$OUT_DIR/$MONSTER_KEY"
RAW_WEBM="$RAW_DIR/raw.webm"
FINAL_MP4="$RAW_DIR/demo.mp4"


mkdir -p "$RAW_DIR"
echo "Running ts-node..."


command -v node >/dev/null || { echo "node is required"; exit 3; }
command -v npx  >/dev/null || { echo "npx is required"; exit 3; }
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 3; }

if ! npx ts-node --esm scripts/record-monster/playwright-demo.ts \
  --monster "$MONSTER_KEY" \
  --base "$BASE_URL" \
  --device "$DEVICE_NAME" \
  --out "$RAW_DIR" \
  --duration "$DURATION_SEC"
then
  echo "ERROR: ts-node failed to run playwright-demo.ts" >&2
  exit 1
fi

ffmpeg -y -i "$RAW_WEBM" -ss "$PREROLL_SEC" -t "$DURATION_SEC" \
  -c:v libx264 -r 30 $FFMPEG_FLAGS -an "$FINAL_MP4"

echo "✅ Demo ready: $FINAL_MP4"
