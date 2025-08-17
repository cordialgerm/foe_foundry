#!/usr/bin/env bash
# mp4-to-gif.sh
# Usage: ./mp4-to-gif.sh input.mp4 output.gif [--start 2.0] [--duration 5]
# Tunables via env:
#   FPS=12 WIDTH=360 COLORS=256 DITHER=bayer DITHER_SCALE=5 LOSSY=60 OPTIMIZE=true

set -euo pipefail

INPUT="${1:-}"
OUTPUT="${2:-}"
shift 2 || true

# Defaults (override via env)
FPS="${FPS:-12}"
WIDTH="${WIDTH:-360}"
COLORS="${COLORS:-256}"          # up to 256
DITHER="${DITHER:-bayer}"         # bayer|sierra2|floyd_steinberg
DITHER_SCALE="${DITHER_SCALE:-5}" # 0–5 for bayer
LOSSY="${LOSSY:-60}"              # gifsicle lossy factor (20–200 typical)
OPTIMIZE="${OPTIMIZE:-true}"      # run gifsicle optimization if available

START=""
DUR=""

# Parse optional args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --start)     START="$2"; shift 2;;
    --duration)  DUR="$2";   shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "${INPUT}" || -z "${OUTPUT}" ]]; then
  echo "Usage: $0 input.mp4 output.gif [--start SECONDS] [--duration SECONDS]" >&2
  exit 1
fi

command -v ffmpeg >/dev/null || { echo "ffmpeg not found"; exit 3; }

# Temp files
PALETTE="$(mktemp /tmp/palette.XXXXXX.png)"
TEMP_GIF="$(mktemp /tmp/temp.XXXXXX.gif)"

# Build common filters
#  - stats_mode=diff improves palette allocation across frames
#  - Lanczos for sharper UI scaling
GEN_FILTER="fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,palettegen=stats_mode=diff:max_colors=${COLORS}"
USE_FILTER="fps=${FPS},scale=${WIDTH}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=${DITHER}"
# Only bayer uses bayer_scale; others ignore the extra option gracefully
USE_FILTER="${USE_FILTER}:bayer_scale=${DITHER_SCALE}"

# Optional trim args
IN_TRIM=()
if [[ -n "${START}" ]]; then IN_TRIM+=(-ss "${START}"); fi
if [[ -n "${DUR}"   ]]; then IN_TRIM+=(-t "${DUR}");   fi

echo "→ Generating palette..."
ffmpeg -y "${IN_TRIM[@]}" -i "${INPUT}" -vf "${GEN_FILTER}" "${PALETTE}"

echo "→ Rendering GIF with palette..."
ffmpeg -y "${IN_TRIM[@]}" -i "${INPUT}" -i "${PALETTE}" \
  -filter_complex "${USE_FILTER}" \
  -loop 0 "${TEMP_GIF}"

rm -f "${PALETTE}"

# Optional optimization with gifsicle if present
if [[ "${OPTIMIZE}" == "true" ]] && command -v gifsicle >/dev/null 2>&1; then
  echo "→ Optimizing with gifsicle (-O3 --lossy=${LOSSY})..."
  gifsicle -O3 --lossy="${LOSSY}" "${TEMP_GIF}" -o "${OUTPUT}"
  rm -f "${TEMP_GIF}"
else
  mv "${TEMP_GIF}" "${OUTPUT}"
fi

# Report size
if command -v stat >/dev/null 2>&1; then
  BYTES=$(stat -f%z "${OUTPUT}" 2>/dev/null || stat -c%s "${OUTPUT}" 2>/dev/null || echo 0)
  echo "✅ GIF saved to ${OUTPUT} ($(awk "BEGIN {printf \"%.2f\", ${BYTES}/1048576}") MB)"
else
  echo "✅ GIF saved to ${OUTPUT}"
fi