from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pydantic.dataclasses import dataclass

from foe_foundry.creatures import MonsterTemplate
from foe_foundry.statblocks import Statblock
from foe_foundry.utils.html import fix_relative_paths, remove_h2_sections

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
        stats: Statblock, template: MonsterTemplate, base_url: str
    ) -> MonsterModel:
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        all_images = []
        for image in template.image_urls.get(stats.variant_key, []):
            relative_image = image.relative_to(Path.cwd() / "docs").as_posix()
            abs_image = urljoin(base_url, relative_image)
            all_images.append(abs_image)

        if len(template.lore_md):
            template_html = _load_monster_html(template.key, base_url)
        else:
            template_html = None

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
