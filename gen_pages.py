# scripts/generate_monster_index.py
from pathlib import Path

import frontmatter
import mkdocs_gen_files

monsters_dir = Path("docs/monsters")

monster_list = []

# Load each monster's frontmatter
for file in monsters_dir.glob("*.md"):
    if file.name == "index.md":
        continue  # Don't self-reference
    post = frontmatter.load(file)
    title = post.get("title", file.stem.replace("-", " ").title())
    monster_list.append((title, file.relative_to(monsters_dir).as_posix()))

# Sort alphabetically
monster_list.sort()

# Create the index content
lines = ["# All Monsters\n", "Browse all monsters below:\n"]

for title, slug in monster_list:
    lines.append(f"- [{title}]({slug}/)")

# Write it into the virtual MkDocs build
with mkdocs_gen_files.open("monsters/index.md", "w") as f:
    f.write("\n".join(lines))
