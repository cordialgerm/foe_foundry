# scripts/generate_monster_index.py
from pathlib import Path

import frontmatter
import mkdocs_gen_files


def generate_topics_index():
    topics_dir = Path("docs/topics")

    topics_list = []

    # Load each monster's frontmatter
    for file in topics_dir.glob("*.md"):
        if file.name == "index.md":
            continue  # Don't self-reference
        post = frontmatter.load(file)  # type: ignore
        title: str = post.get("short_title", file.stem.replace("-", " ").title())  # type: ignore
        topics_list.append((title, file.relative_to(topics_dir).as_posix()))

    # Sort alphabetically
    topics_list.sort()

    # Create the index content
    lines = ["# All Topics\n", "Browse all topics below:\n"]

    for title, slug in topics_list:
        lines.append(f"- [{title}]({slug}/)")

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open("topics/index.md", "w") as f:
        f.write("\n".join(lines))
