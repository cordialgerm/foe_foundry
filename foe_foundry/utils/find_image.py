from pathlib import Path


def find_image(name: str) -> list[Path]:
    img_dir = Path(__file__).parent.parent.parent / "foe_foundry_ui" / "public" / "img"

    extensions = [
        ".png",
        ".tif",
        ".jpeg",
        ".gif",
    ]

    paths = []

    for ext in extensions:
        paths.extend(img_dir.rglob(f"**/{name}{ext}"))

    return paths
