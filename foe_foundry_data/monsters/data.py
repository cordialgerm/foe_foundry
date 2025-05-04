from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import CreatureTemplate
from foe_foundry.jinja import render_statblock_fragment
from foe_foundry.statblocks import Statblock
from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections


def _load_monster_html(template_key: str, base_url: str) -> str | None:
    html_path = Path.cwd() / "site" / "monsters" / template_key / "index.html"
    if not html_path.exists():
        return None
    bs4 = BeautifulSoup(html_path.read_text(), "html.parser")
    monster_html = str(bs4.find("div", class_="pamphlet-main"))

    h2_ids_to_remove = [f"{template_key}-statblocks"]
    cleaned_html = remove_h2_sections(monster_html, h2_ids_to_remove)
    cleaned_html = fix_relative_paths(cleaned_html, base_url)
    return cleaned_html


@dataclass(kw_only=True)
class CreatureTemplateModel:
    template_key: str
    name: str
    template_html: str | None
    images: list[str]

    @staticmethod
    def from_template(
        template: CreatureTemplate, base_url: str
    ) -> CreatureTemplateModel:
        if not base_url.endswith("/"):
            base_url += "/"

        all_images = []
        for _, images in template.image_urls.items():
            for image in images:
                relative_image = image.relative_to(Path.cwd() / "docs").as_posix()
                abs_image = urljoin(base_url, relative_image)
                all_images.append(abs_image)

        monster_html = _load_monster_html(template.key, base_url)
        return CreatureTemplateModel(
            template_key=template.key,
            name=template.name,
            template_html=monster_html,
            images=all_images,
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

    @staticmethod
    def from_monster(
        stats: Statblock, template: CreatureTemplate, base_url: str
    ) -> MonsterModel:
        all_images = []
        for image in template.image_urls.get(stats.variant_key, []):
            relative_image = image.relative_to(Path.cwd() / "docs").as_posix()
            abs_image = urljoin(base_url, relative_image)
            all_images.append(abs_image)

        template_html = _load_monster_html(template.key, base_url)

        statblock_html = render_statblock_fragment(stats)

        return MonsterModel(
            name=stats.name,
            cr=stats.cr,
            template_key=stats.template_key,
            variant_key=stats.variant_key,
            statblock_html=statblock_html,
            template_html=template_html,
            images=all_images,
        )
