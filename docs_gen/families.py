# scripts/generate_monster_index.py
from pathlib import Path

import frontmatter
import mkdocs_gen_files


def generate_families_index():
    monsters_dir = Path("docs/families")

    monster_list = []

    # Load each monster's frontmatter
    for file in monsters_dir.glob("*.md"):
        if file.name == "index.md":
            continue  # Don't self-reference
        post = frontmatter.load(file)  # type: ignore
        title: str = post.get("short_title", file.stem.replace("-", " ").title())  # type: ignore

        monster_list.append((title, file.relative_to(monsters_dir).as_posix()))

    # Sort alphabetically
    monster_list.sort()

    # Create the index content
    lines = [
        "---",
        "title: Monster Families | Foe Foundry",
        "description: Explore 5E monster families and their unique abilities. Discover how to use them in your game and find the perfect monster for your next encounter.",
        "hide:",
        "   - toc",
        "   - backlinks",
        "---",
        "[[@Subscribe to the Newsletter]]\n",
        "---",
        "# All Monster Families\n",
        "Browse all monster families below:\n",
    ]

    for title, slug in monster_list:
        lines.append(f"- [{title}]({slug}/)")

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open("families/index.md", "w") as f:
        f.write("\n".join(lines))
