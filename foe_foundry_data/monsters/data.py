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
)
from foe_foundry.powers import Power, PowerLoadout
from foe_foundry.statblocks import Statblock
from foe_foundry.utils import name_to_key
from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections
from foe_foundry.utils.image import (
    get_dominant_edge_color,
    has_transparent_edges,
    is_grayscaleish,
)

from ..jinja import render_statblock_fragment


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
class PowerRef:
    key: str
    name: str
    power_category: str
    source: str
    theme: str
    icon: str

    @staticmethod
    def from_power(power: Power) -> PowerRef:
        return PowerRef(
            key=power.key,
            name=power.name,
            power_category=power.power_category.name,
            source=power.source or "UNKNOWN",
            theme=power.theme or "UNKNOWN",
            icon=power.icon or "",
        )


@dataclass(kw_only=True)
class PowerLoadoutModel:
    key: str
    name: str
    flavor_text: str
    selection_count: int
    locked: bool
    replace_with_species_powers: bool
    powers: List[PowerRef]

    @staticmethod
    def from_loadout(loadout: PowerLoadout):
        return PowerLoadoutModel(
            key=loadout.key,
            name=loadout.name,
            flavor_text=loadout.flavor_text,
            selection_count=loadout.selection_count,
            locked=loadout.locked,
            replace_with_species_powers=loadout.replace_with_species_powers,
            powers=[PowerRef.from_power(power) for power in loadout.powers],
        )


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

    statblock_html: str
    template_html: str | None
    has_lore: bool
    images: list[str]
    loadouts: list[PowerLoadoutModel]
    primary_image: str | None
    background_image: str | None = None
    primary_image_has_transparent_edges: bool
    primary_image_is_grayscaleish: bool
    primary_image_background_color: str | None = None
    create_date: datetime
    modified_date: datetime

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
            statblock_html=statblock_html,
            template_html=template_html,
            has_lore=template.lore_md is not None,
            images=all_images,
            loadouts=loadouts,
            primary_image=primary_image,
            background_image=urljoin(base_url, background_image),
            primary_image_has_transparent_edges=primary_image_has_transparent_edges,
            primary_image_is_grayscaleish=primary_image_is_grayscaleish,
            primary_image_background_color=primary_image_background_color,
            create_date=template.create_date,
            modified_date=template.modified_date,
        )
