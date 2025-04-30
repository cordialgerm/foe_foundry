# scripts/generate_monster_index.py
from pathlib import Path

import frontmatter
import mkdocs_gen_files


def generate_monster_index():
    monsters_dir = Path("docs/monsters")

    monster_list = []

    # Load each monster's frontmatter
    for file in monsters_dir.glob("*.md"):
        if file.name == "index.md":
            continue  # Don't self-reference
        post = frontmatter.load(file)  # type: ignore
        title: str = post.get("short_title", file.stem.replace("-", " ").title())  # type: ignore

        if title.endswith(" - Summoned with Foe Foundry"):
            title = title[: -len(" - Summoned with Foe Foundry")]

        monster_list.append((title, file.relative_to(monsters_dir).as_posix()))

    # Sort alphabetically
    monster_list.sort()

    # Create the index content
    lines = [
        "---",
        "title: Monsters",
        "hide:",
        "   - toc",
        "---",
        "# All Monsters\n",
        "Browse all monsters below:\n",
    ]

    for title, slug in monster_list:
        lines.append(f"- [{title}]({slug}/)")

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open("monsters/index.md", "w") as f:
        f.write("\n".join(lines))
