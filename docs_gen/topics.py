# scripts/generate_monster_index.py
from pathlib import Path

import frontmatter
import mkdocs_gen_files

from .types import FilesToGenerate


def generate_topics_content() -> FilesToGenerate:
    """Generate topics index content without writing to mkdocs_gen_files.

    Returns FilesToGenerate with the files to be written.
    """
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
    lines = [
        "---",
        "title: Topics | Foe Foundry",
        "description: Learn more about Foe Foundry including design philosophy, custom powers, and custom conditions to support hundreds of unique monster variations.",
        "hide:",
        "   - toc",
        "   - backlinks",
        "---",
        "# All Topics\n",
        "Browse all topics below:\n",
    ]

    for title, slug in topics_list:
        lines.append(f"- [{title}]({slug}/)")

    return FilesToGenerate(name="topics", files={"topics/index.md": "\n".join(lines)})


def generate_topics_index():
    """Generate topics index and write directly to mkdocs_gen_files."""
    result = generate_topics_content()

    # Write it into the virtual MkDocs build
    for filename, content in result.files.items():
        with mkdocs_gen_files.open(filename, "w") as f:
            f.write(content)
