from pathlib import Path


def find_image(name: str) -> list[Path]:
    img_dir = Path(__file__).parent.parent.parent / "docs" / "img"

    extensions = [
        ".png",
        ".jpeg",
        ".gif",
        ".webp",
    ]

    paths = []

    for ext in extensions:
        paths.extend(img_dir.rglob(f"**/{name}{ext}"))

    return paths


def find_lore(name: str) -> list[Path]:
    lore_dir = Path(__file__).parent.parent.parent / "docs" / "monsters"

    paths = []

    for path in lore_dir.rglob(f"**/{name}.md"):
        paths.append(path)

    return paths
