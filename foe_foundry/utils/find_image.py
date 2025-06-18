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


def find_lore(name: str) -> Path | None:
    lore_dir = Path(__file__).parent.parent.parent / "docs" / "monsters"

    paths = []

    for path in lore_dir.rglob(f"**/{name}.md"):
        paths.append(path)

    if len(paths) > 1:
        raise ValueError(f"Multiple lore files found for {name}: {paths}")
    elif len(paths) == 0:
        return None

    return paths[0]
