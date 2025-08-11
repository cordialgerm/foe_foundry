from pathlib import Path


def find_monster_image(name: str) -> list[Path]:
    img_dir = Path(__file__).parent.parent.parent / "docs" / "img" / "monsters"
    # Prioritize .webp, but allow all extensions
    extensions = [".webp", ".png", ".jpeg", ".gif"]
    extensions_set = set(extensions)

    # Use rglob with name as part of the pattern for efficiency
    candidates = img_dir.rglob(f"{name}.*")
    matches = [f for f in candidates if f.is_file() and f.suffix in extensions_set]

    # Sort so .webp comes first, then others in order
    matches.sort(
        key=lambda p: extensions.index(p.suffix) if p.suffix in extensions else 99
    )
    return matches


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
