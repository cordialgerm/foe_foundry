from __future__ import annotations

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
from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections
from foe_foundry.utils.image import has_transparent_edges

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
    power_type: str
    source: str
    theme: str
    icon: str

    @staticmethod
    def from_power(power: Power) -> PowerRef:
        return PowerRef(
            key=power.key,
            name=power.name,
            power_type=power.power_type.name,
            source=power.source or "UNKNOWN",
            theme=power.theme or "UNKNOWN",
            icon=power.icon or "",
        )


@dataclass(kw_only=True)
class PowerLoadoutModel:
    name: str
    flavor_text: str
    selection_count: int
    locked: bool
    replace_with_species_powers: bool
    powers: List[PowerRef]

    @staticmethod
    def from_loadout(loadout: PowerLoadout):
        return PowerLoadoutModel(
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
    template_key: str
    variant_key: str

    statblock_html: str
    template_html: str | None
    images: list[str]
    loadouts: list[PowerLoadoutModel]
    primary_image: str | None
    primary_image_has_transparent_edges: bool

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
        else:
            primary_image = None
            primary_image_has_transparent_edges = False

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

        return MonsterModel(
            name=stats.name,
            cr=stats.cr,
            template_key=stats.template_key,
            variant_key=stats.variant_key,
            statblock_html=statblock_html,
            template_html=template_html,
            images=all_images,
            loadouts=loadouts,
            primary_image=primary_image,
            primary_image_has_transparent_edges=primary_image_has_transparent_edges,
        )
