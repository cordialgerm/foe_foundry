from pathlib import Path

from foe_foundry.creatures import AllTemplates
from foe_foundry.utils import name_to_key
from foe_foundry.utils.monster_content import (
    extract_monster_hyperlinks,
    extract_tagline,
    extract_yaml_frontmatter,
    strip_yaml_frontmatter,
)

from ..base import MonsterInfoModel
from ..refs import MonsterRefResolver
from .data import MonsterFamilyModel


def get_family_icon(family_key: str) -> str:
    """Get appropriate icon for a monster family."""
    icon_mapping = {
        "criminals": "bandit",
        "fanatics-and-faithful": "prayer",
        "giants": "giant",
        "monstrosities": "monster-grasp",
        "orcs-and-goblinoids": "goblin-head",
        "soldiers-and-fighters": "sword-brandish",
        "undead": "skull-crossed-bones",
    }
    return icon_mapping.get(family_key, "monster-grasp")

ref_resolver = MonsterRefResolver()


def load_families() -> list[MonsterFamilyModel]:
    families_dir = Path.cwd() / "docs" / "families"

    families = []
    for md_file in families_dir.glob("*.md"):
        with md_file.open() as f:
            content = f.read()
            name = md_file.stem
            frontmatter = extract_yaml_frontmatter(content)
            is_monster_family = frontmatter.get("is_monster_family", False)
            if not is_monster_family:
                continue
            markdown_content = strip_yaml_frontmatter(content)
            title = frontmatter.get("family_name", frontmatter.get("short_title"))
            if not isinstance(title, str):
                raise ValueError(
                    f"Invalid title for family '{name}': {title}. Expected a string."
                )
            tag_line = extract_tagline(content)
            if tag_line is None:
                raise ValueError(
                    f"Tagline not found for family '{name}'. Ensure it is defined in the markdown content."
                )
            monster_links = extract_monster_hyperlinks(markdown_content)

            monsters = []
            template_keys: set[str] = set()
            for link in monster_links:
                ref = ref_resolver.resolve_monster_ref(link)
                if ref is None:
                    raise ValueError(
                        f"Monster reference '{link}' in family '{title}' could not be resolved."
                    )
                template = ref.template
                template_keys.add(template.key)

            templates = [t for t in AllTemplates if t.key in template_keys]
            for template in templates:
                for monster in template.monsters:
                    monsters.append(
                        MonsterInfoModel(
                            key=monster.key,
                            name=monster.name,
                            cr=monster.cr,
                            template=template.key,
                        )
                    )

            families.append(
                MonsterFamilyModel(
                    key=name_to_key(name),
                    name=title,
                    tag_line=tag_line,
                    icon=get_family_icon(name_to_key(name)),
                    monsters=monsters,
                )
            )

    return families
