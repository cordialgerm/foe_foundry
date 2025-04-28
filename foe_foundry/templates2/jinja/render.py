import shutil
from pathlib import Path

import numpy as np

from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
)
from foe_foundry.markdown import markdown

from ...statblocks import Statblock
from .data import MonsterTemplateData
from .dict import AccessTrackingDict
from .env import JinjaEnv, load_template_from_markdown


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
    md = markdown(lore_md_raw)

    # render the entire pamphlet
    pamphlet_context: dict = dict(header=md.header, toc=md.toc, html=md.html)
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
    lore_md = markdown(lore_md_raw)

    # check if all statblocks and images were used
    unused_statblocks = [v for _, v in access_tracking_statblocks.get_unused().items()]
    if len(unused_statblocks) > 0 and template.name != "Mage":  # TEMP
        raise ValueError("Unused statblocks and/or images")

    # render the entire pamphlet
    pamphlet_context: dict = dict(
        header=lore_md.header, toc=lore_md.toc, html=lore_md.html
    )
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
