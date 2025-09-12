from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import (
    CreatureSpecies,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    TemplatesByKey,
)
from foe_foundry.environs import Region
from foe_foundry.environs.affinity import Affinity
from foe_foundry.statblocks import Statblock
from foe_foundry.tags import TagDefinition
from foe_foundry.utils import name_to_key
from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections
from foe_foundry.utils.image import (
    get_dominant_edge_color,
    has_transparent_edges,
    is_grayscaleish,
)

from ..base import (
    MonsterInfoModel,
    MonsterTagInfo,
    PowerLoadoutModel,
)
from ..jinja import render_statblock_fragment
from ..monster_families import MonsterFamilies


@dataclass(kw_only=True)
class RelatedMonsterModel(MonsterInfoModel):
    same_template: bool
    family: str | None


def _convert_markdown_to_html(markdown_text: str | None) -> str | None:
    """Convert markdown to HTML, handling the import locally to avoid circular dependencies."""
    if markdown_text is not None and len(markdown_text):
        from ..markdown import markdown

        return markdown(markdown_text).html
    return None


def _load_monster_html(template_key: str, base_url: str) -> str | None:
    html_path = (
        Path(__file__).parent.parent.parent
        / "site"
        / "monsters"
        / template_key
        / "index.html"
    )
    if not html_path.exists():
        return None
    bs4 = BeautifulSoup(html_path.read_text(), "html.parser")
    monster_html = str(bs4.find("div", class_="pamphlet-main"))

    h2_ids_to_remove = [f"{template_key}-statblocks"]
    cleaned_html = remove_h2_sections(monster_html, h2_ids_to_remove)
    cleaned_html = fix_relative_paths(cleaned_html, base_url)
    return cleaned_html


@dataclass(kw_only=True)
class MonsterModel:
    name: str
    cr: float
    size: str
    tag_line: str
    creature_type: str
    template_name: str
    template_key: str
    variant_name: str
    variant_key: str
    tags: List[MonsterTagInfo]

    statblock_html: str
    template_html: str | None
    overview_html: str | None
    encounter_html: str | None
    has_lore: bool
    images: list[str]
    loadouts: list[PowerLoadoutModel]
    related_monsters: list[RelatedMonsterModel]
    primary_image: str | None
    background_image: str | None = None
    primary_image_has_transparent_edges: bool
    primary_image_is_grayscaleish: bool
    primary_image_background_color: str | None = None
    create_date: datetime
    family_keys: list[str] | None = None  # Support multiple families

    @property
    def key(self) -> str:
        return name_to_key(self.name)

    @staticmethod
    def from_monster(
        stats: Statblock,
        template: MonsterTemplate,
        variant: MonsterVariant,
        monster: Monster,
        species: CreatureSpecies | None,
        base_url: str,
    ) -> MonsterModel:
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        def convert_img(image: Path) -> str:
            relative_image = image.relative_to(Path.cwd() / "docs").as_posix()
            abs_image = urljoin(base_url, relative_image)
            return abs_image

        all_images = [
            convert_img(img) for img in template.image_urls.get(stats.variant_key, [])
        ]

        if template.primary_image_url is not None:
            primary_image = convert_img(template.primary_image_url)
            primary_image_has_transparent_edges = has_transparent_edges(
                template.primary_image_url
            )

            if not primary_image_has_transparent_edges:
                primary_image_is_grayscaleish = is_grayscaleish(
                    template.primary_image_url
                )
                primary_image_background_color = get_dominant_edge_color(
                    template.primary_image_url
                )
            else:
                primary_image_is_grayscaleish = False
                primary_image_background_color = None

        else:
            primary_image = None
            primary_image_has_transparent_edges = False
            primary_image_is_grayscaleish = False
            primary_image_background_color = None

        if template.lore_md is not None and len(template.lore_md):
            template_html = _load_monster_html(template.key, base_url)
        else:
            template_html = None

        if template.overview_md is not None and len(template.overview_md):
            overview_html = _convert_markdown_to_html(template.overview_md)
        else:
            overview_html = None

        if template.encounter_md is not None and len(template.encounter_md):
            encounter_html = _convert_markdown_to_html(template.encounter_md)
        else:
            encounter_html = None

        statblock_html = render_statblock_fragment(stats)

        settings = template._settings_for_variant(
            variant=variant, monster=monster, species=species
        )
        power_selection = template.choose_powers(settings=settings)
        loadouts = [
            PowerLoadoutModel.from_loadout(loadout)
            for loadout in power_selection.loadouts
        ]

        background_image = (
            f"img/backgrounds/textures/{stats.creature_type.value.lower()}.webp"
        )
        background_image_path = Path.cwd() / "docs" / background_image
        if not background_image_path.exists():
            background_image = None

        # monsters in the same template are always related
        related_monsters = [
            RelatedMonsterModel(
                key=m.key,
                name=m.name,
                cr=m.cr,
                template=template.name,
                family=None,
                same_template=True,
            )
            for m in template.monsters
        ]
        related_monster_keys = {m.key for m in related_monsters}

        # Also look for any monsters that are in the same family as this monster
        families = [
            f
            for f in MonsterFamilies.families
            if stats.key in {m.key for m in f.monsters}
        ]

        # Get all families this monster belongs to (support multiple families)
        monster_family_keys = [f.key for f in families] if families else None

        for family in families:
            for m in family.monsters:
                if m.key not in related_monster_keys:
                    related_monsters.append(
                        RelatedMonsterModel(
                            key=m.key,
                            name=m.name,
                            cr=m.cr,
                            template=TemplatesByKey[m.template].name,
                            family=family.name,
                            same_template=False,
                        )
                    )

        # Extract tags from statblock and sort them
        tag_infos = []
        for monster_tag in stats.tags:
            # Get key from definition if available, otherwise derive from tag name
            tag_infos.append(
                MonsterTagInfo(
                    tag=monster_tag.name,
                    key=monster_tag.key,
                    tag_type=monster_tag.category,
                    description=monster_tag.description,
                    icon=monster_tag.icon,
                    color=monster_tag.color,
                )
            )

        if template and hasattr(template, "environments") and template.environments:
            for env, affinity in template.environments:
                # Only add region tags for native and common affinities (not rare or unknown)
                if isinstance(env, Region) and affinity in {
                    Affinity.native,
                    Affinity.common,
                }:
                    region_tag = TagDefinition.from_region(env)
                    tag_infos.append(
                        MonsterTagInfo(
                            tag=region_tag.name,
                            key=region_tag.key,
                            tag_type=region_tag.category,
                            description=region_tag.description,
                            icon=region_tag.icon,
                            color=region_tag.color,
                        )
                    )

        # Sort tags by desired order: Creature Type, Role(s), Spellcaster, Tier, Legendary, Damage Type(s)
        def tag_sort_order(tag: MonsterTagInfo) -> tuple:
            type_priority = {
                "creature_type": 1,
                "species": 2,
                "monster_role": 3,
                "theme": 4,
                "cr_tier": 5,
                "legendary": 6,
                "damage_type": 7,
                "region": 8,
            }
            # Get priority, default to 9 for unknown types
            priority = type_priority.get(tag.tag_type, 9)
            # Secondary sort by tag name for consistent ordering within same type
            return (priority, tag.tag)

        tag_infos.sort(key=tag_sort_order)

        return MonsterModel(
            name=stats.name,
            cr=stats.cr,
            size=stats.size.name,
            tag_line=template.tag_line,
            creature_type=stats.creature_type.name,
            template_key=stats.template_key,
            template_name=template.name,
            variant_key=stats.variant_key,
            variant_name=variant.name,
            tags=tag_infos,
            statblock_html=statblock_html,
            template_html=template_html,
            overview_html=overview_html,
            encounter_html=encounter_html,
            has_lore=template.lore_md is not None,
            images=all_images,
            loadouts=loadouts,
            related_monsters=related_monsters,
            primary_image=primary_image,
            background_image=urljoin(base_url, background_image),
            primary_image_has_transparent_edges=primary_image_has_transparent_edges,
            primary_image_is_grayscaleish=primary_image_is_grayscaleish,
            primary_image_background_color=primary_image_background_color,
            create_date=template.create_date,
            family_keys=monster_family_keys,
        )
