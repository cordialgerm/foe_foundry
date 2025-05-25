import os
import re
from pathlib import Path

from PIL import Image, PngImagePlugin

# Configuration
image_dir = (
    Path(__file__).parent.parent / "docs" / "img"
)  # directory where original images are stored
markdown_dir = Path(__file__).parent.parent / "docs"  # directory with your .md files
output_dir = image_dir / "monsters"  # output location for resized webp files
output_dir.mkdir(parents=True, exist_ok=True)

# Set target size (resize only if larger)
MAX_SIZE = (1200, 1200)

PngImagePlugin.MAX_TEXT_CHUNK = (
    100 * 1024 * 1024
)  # Optional if you want to just up the limit


# Step 1: Convert and resize images
def convert_images_to_webp():
    converted = {}
    for img_path in image_dir.glob("*"):
        if img_path.suffix.lower() not in [".png", ".jpg", ".jpeg"]:
            continue

        img = Image.open(img_path)
        img.load()  # Ensure full load before copying

        # Check if image has transparency
        has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

        if has_alpha:
            clean_img = Image.new("RGBA", img.size)
        else:
            clean_img = Image.new("RGB", img.size)

        # Strip metadata by copying into a fresh image
        clean_img.paste(img)

        clean_img.thumbnail(MAX_SIZE)
        new_name = img_path.stem + ".webp"
        new_path = output_dir / new_name
        clean_img.save(new_path, "WEBP")
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

            new_url = conversion_map.get(filename)
            if new_url is None:
                continue

            if path.startswith("img/"):
                new_path = "img/" + new_url
            elif path.startswith("../img/"):
                new_path = "../img/" + new_url
            elif path.startswith("./img/"):
                new_path = "./img/" + new_url
            else:
                continue

            new_text = new_text.replace(f"]({path})", f"]({new_path})")

        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            print(f"Updated: {md_file}")


if __name__ == "__main__":
    mapping = convert_images_to_webp()
    update_markdown_files(mapping)
