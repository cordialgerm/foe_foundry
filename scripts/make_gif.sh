#!/usr/bin/env bash
# mp4-to-gif.sh
# Usage: ./mp4-to-gif.sh input.mp4 output.gif

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: $0 input.mp4 output.gif"
  exit 1
fi

# Temp palette file
PALETTE=$(mktemp /tmp/palette.png)

# Generate a palette for good colors
ffmpeg -i "$INPUT" -vf "fps=12,scale=360:-1:flags=lanczos,palettegen" -y "$PALETTE"

# Apply the palette to create the GIF
ffmpeg -i "$INPUT" -i "$PALETTE" -filter_complex "fps=12,scale=360:-1:flags=lanczos[x];[x][1:v]paletteuse" -y "$OUTPUT"

rm "$PALETTE"

echo "✅ GIF saved to $OUTPUT"