import shutil
from pathlib import Path

import numpy as np
from bs4 import BeautifulSoup
from markdown import Markdown

from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
)

from ...statblocks import Statblock
from .data import MonsterTemplateData
from .dict import AccessTrackingDict
from .env import JinjaEnv, load_template_from_markdown
from .monster_ref import TestMonsterRefResolver


def render_statblock_fragment(stats: Statblock) -> str:
    """Renders a statblock HTML fragment for a single statblock"""

    template = JinjaEnv.get_template("statblock.html.j2")
    data = MonsterTemplateData.from_statblock(stats)
    context = dict(statblock=data.to_dict())
    html_raw = template.render(context)
    return html_raw


def render_theme_pamphlet(theme: str, path: Path) -> Path:
    family_dir = Path(__file__).parent.parent.parent.parent / "content" / "themes"
    family_path = family_dir / f"{theme}.md"

    # get lore template
    lore_template_str = family_path.read_text().strip()
    if len(lore_template_str) == 0:
        lore_template_str = f"# {theme}\n\nNo Lore Available"

    lore_template = load_template_from_markdown(lore_template_str)

    # render statblocks and images into lore template
    lore_context: dict = dict()
    lore_md_raw = lore_template.render(lore_context)
    header, toc, html = _markdown_with_toc(lore_md_raw)

    # render the entire pamphlet
    pamphlet_context: dict = dict(header=header, toc=toc, html=html)
    jinja_template = JinjaEnv.get_template("pamphlet.html.j2")
    html_raw = jinja_template.render(pamphlet_context)

    with path.open("w") as f:
        f.write(html_raw)

    css_dir_src = Path(__file__).parent.parent / "css"
    css_dir_dst = path.parent / "css"
    css_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=css_dir_src, dst=css_dir_dst, dirs_exist_ok=True)

    img_dir_src = Path(__file__).parent.parent / "img"
    img_dir_dst = path.parent / "img"
    img_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=img_dir_src, dst=img_dir_dst, dirs_exist_ok=True)

    return path


def render_statblock_pamphlet(stats: Statblock, path: Path) -> Path:
    """Renders a PDF-friendly pamphlet of a single statblock"""

    statblock_html = render_statblock_fragment(stats)

    # render the entire pamphlet
    pamphlet_context: dict = dict(header=stats.name, toc=None, html=statblock_html)
    jinja_template = JinjaEnv.get_template("pamphlet.html.j2")
    html_raw = jinja_template.render(pamphlet_context)

    with path.open("w") as f:
        f.write(html_raw)

    css_dir_src = Path(__file__).parent.parent / "css"
    css_dir_dst = path.parent / "css"
    css_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=css_dir_src, dst=css_dir_dst, dirs_exist_ok=True)

    img_dir_src = Path(__file__).parent.parent / "img"
    img_dir_dst = path.parent / "img"
    img_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=img_dir_src, dst=img_dir_dst, dirs_exist_ok=True)

    return path


def render_creature_template_pamphlet(template: CreatureTemplate, path: Path) -> Path:
    """Renders a PDF-friendly pamphlet of lore, images, and statblocks for a creature template"""

    def rng_factory():
        return np.random.default_rng()

    # render statblocks
    statblocks: dict = {}
    for variant in template.variants:
        for suggested_cr in variant.suggested_crs:
            stats = template.generate(
                GenerationSettings(
                    creature_name=suggested_cr.name,
                    creature_template=template.name,
                    variant=variant,
                    cr=suggested_cr.cr,
                    species=None,
                    is_legendary=suggested_cr.is_legendary,
                    rng=rng_factory(),
                )
            ).finalize()
            statblocks[stats.key] = MonsterTemplateData.from_statblock(stats)

    # track which statblocks get used by Jinja so we know if we forgot to include anything
    access_tracking_statblocks = AccessTrackingDict(**statblocks)

    # get lore template
    lore_template_str = template.lore_md.strip()
    if len(lore_template_str) == 0:
        lore_template_str = f"# {template.name}\n\nNo Lore Available"

    lore_template = load_template_from_markdown(lore_template_str)

    # render statblocks and images into lore template
    lore_context: dict = dict(statblocks=access_tracking_statblocks)
    lore_md_raw = lore_template.render(lore_context)
    header, toc, html = _markdown_with_toc(lore_md_raw)

    # check if all statblocks and images were used
    unused_statblocks = [v for _, v in access_tracking_statblocks.get_unused().items()]
    if len(unused_statblocks) > 0 and template.name != "Mage":  # TEMP
        raise ValueError("Unused statblocks and/or images")

    # render the entire pamphlet
    pamphlet_context: dict = dict(header=header, toc=toc, html=html)
    jinja_template = JinjaEnv.get_template("pamphlet.html.j2")
    html_raw = jinja_template.render(pamphlet_context)

    with path.open("w") as f:
        f.write(html_raw)

    css_dir_src = Path(__file__).parent.parent / "css"
    css_dir_dst = path.parent / "css"
    css_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=css_dir_src, dst=css_dir_dst, dirs_exist_ok=True)

    img_dir_src = Path(__file__).parent.parent / "img"
    img_dir_dst = path.parent / "img"
    img_dir_dst.mkdir(exist_ok=True, parents=True)
    shutil.copytree(src=img_dir_src, dst=img_dir_dst, dirs_exist_ok=True)

    return path


def _markdown_with_toc(text: str, strip_header: bool = True) -> tuple[str, str, str]:
    """Renders a markdown string into HTML and returns the header, toc, and html"""

    # if text starts with an h1 header, remove that line
    if text.startswith("# "):
        lines = text.splitlines(keepends=True)
        header_line = lines[0]
        header = header_line[1:].strip()
        if strip_header:
            lines = lines[1:]
        text = "".join(lines)
    else:
        header = ""

    md = Markdown(
        extensions=["toc", "tables"],
        extension_configs={
            "toc": {
                "permalink": True  # adds a link symbol next to headers
            }
        },
    )
    html = md.convert(text)
    toc = md.toc  # type: ignore

    # Replace all monster references with links
    soup = BeautifulSoup(html, "html.parser")
    resolver = TestMonsterRefResolver()

    for strong_tag in soup.find_all(["strong", "b"]):
        monster_ref_markup = resolver.resolve_monster_ref(strong_tag.text)
        if monster_ref_markup is None:
            continue

        monster_ref = BeautifulSoup(str(monster_ref_markup), "html.parser")
        strong_tag.replace_with(monster_ref)

    html = str(soup)

    return header, toc, html
