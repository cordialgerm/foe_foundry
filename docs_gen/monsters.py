from pathlib import Path

import mkdocs_gen_files

from foe_foundry.creatures import AllTemplates, MonsterTemplate

from .types import FilesToGenerate


def generate_monsters_with_no_lore_content() -> FilesToGenerate:
    """Generate monster files content without writing to mkdocs_gen_files.

    Returns FilesToGenerate with all the files to be written.
    """
    files = {}

    for template in AllTemplates:
        # if the template already has lore then skip it
        if template.lore_md is not None and len(template.lore_md):
            continue

        content = generate_monster_file_content(template)
        files[f"monsters/{template.key}.md"] = content

    return FilesToGenerate(name="monsters", files=files)


def generate_monster_file_content(creature: MonsterTemplate) -> str:
    """Generate content for a monster file without writing to mkdocs_gen_files."""
    docs_dir = Path(__file__).parent.parent / "docs"
    img_url = (
        str(creature.primary_image_url.relative_to(docs_dir))
        if creature.primary_image_url
        else "img/icons/favicon.webp"
    )
    img_class = "{ .monster-image-small }"

    lines = [
        "---",
        f"title: {creature.name} | Foe Foundry",
        f"description: Discover the {creature.name} for your next 5E or TTRPG monster.\n",
        f"image: {img_url}",
        "---\n",
        f"# {creature.name}\n\n",
        "We're still working on the lore for this creature, but the stats are ready to go!\n\n",
        f"![{creature.name}](../{img_url}){img_class}\n\n",
        f"## {creature.name} Statblocks\n\n",
    ]

    for variant in creature.variants:
        for monster in variant.monsters:
            lines.append(f"### {monster.name}\n")
            lines.append(f"[[!{monster.name}]]\n")
            lines.append(f"[[${monster.name}]]\n")
            lines.append("---\n")

    return "\n".join(lines)


def generate_monsters_with_no_lore():
    """Generate monster files and write directly to mkdocs_gen_files."""
    result = generate_monsters_with_no_lore_content()

    # Write all files into the virtual MkDocs build
    for filename, content in result.files.items():
        with mkdocs_gen_files.open(filename, "w") as f:
            f.write(content)


def generate_monster_file(creature: MonsterTemplate):
    """Generate monster file and write directly to mkdocs_gen_files."""
    content = generate_monster_file_content(creature)

    # Write it into the virtual MkDocs build
    with mkdocs_gen_files.open(f"monsters/{creature.key}.md", "w") as f:
        f.write(content)
