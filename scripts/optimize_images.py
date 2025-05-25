import os
import re
from pathlib import Path

from PIL import Image

# Configuration
image_dir = (
    Path(__file__).parent.parent / "docs" / "img"
)  # directory where original images are stored
markdown_dir = Path(__file__).parent.parent / "docs"  # directory with your .md files
output_dir = image_dir / "webp"  # output location for resized webp files
output_dir.mkdir(parents=True, exist_ok=True)

# Set target size (resize only if larger)
MAX_SIZE = (1200, 1200)


# Step 1: Convert and resize images
def convert_images_to_webp():
    converted = {}
    for img_path in image_dir.glob("*"):
        if img_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            continue

        img = Image.open(img_path)
        img.thumbnail(MAX_SIZE)
        new_name = img_path.stem + ".webp"
        new_path = output_dir / new_name
        img.save(new_path, "WEBP")
        converted[img_path.name] = f"{output_dir.name}/{new_name}"
    return converted


# Step 2: Update markdown references
def update_markdown_files(conversion_map):
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    for md_file in markdown_dir.rglob("**/*.md"):
        text = md_file.read_text(encoding="utf-8")
        new_text = text

        for match in pattern.finditer(text):
            alt_text, path = match.groups()
            filename = os.path.basename(path)
            if filename in conversion_map:
                new_url = conversion_map[filename]
                new_text = new_text.replace(f"]({path})", f"]({new_url})")

        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            print(f"Updated: {md_file}")


if __name__ == "__main__":
    mapping = convert_images_to_webp()
    update_markdown_files(mapping)
