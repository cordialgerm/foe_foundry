from io import BytesIO  # noqa
from pathlib import Path
from markdown import markdown
import shutil

import numpy as np
from PIL import Image  # noqa

from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
)

from ...statblocks import Statblock
from .data import MonsterTemplateData
from .dict import AccessTrackingDict
from .env import JinjaEnv
from .utilities import resize_image_as_base64_png


def render_statblock_fragment(stats: Statblock) -> str:
    """Renders a statblock HTML fragment for a single statblock"""

    template = JinjaEnv.get_template("statblock.html.j2")
    data = MonsterTemplateData.from_statblock(stats)
    context = dict(statblock=data.to_dict())
    html_raw = template.render(context)
    return html_raw


def render_pamphlet(template: CreatureTemplate, path: Path) -> Path:
    """Renders a PDF-friendly pamphlet of lore, images, and statblocks"""

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

    # load images for each statblock
    images: dict[str, list[dict]] = {}
    for variant_key, image_paths in template.image_urls.items():
        variant_images = []
        for image_path in image_paths:
            base64_str = resize_image_as_base64_png(image_path)
            variant_images.append(dict(image_ext="png", image_base64=base64_str))
        images[variant_key] = variant_images

    # track which images get used by Jinja so we know if we forgot to include anything
    access_tracking_images = AccessTrackingDict(**images)

    # get lore template
    lore_template_str = template.lore_md.strip()
    if len(lore_template_str) == 0:
        lore_template_str = f"# {template.name}\n\nNo Lore Available"

    lore_template = JinjaEnv.from_string(lore_template_str)

    # render statblocks and images into lore template
    lore_context: dict = dict(
        statblocks=access_tracking_statblocks, images=access_tracking_images
    )
    lore_md_raw = lore_template.render(lore_context)
    lore_html_raw = markdown(lore_md_raw, extensions=["toc", "tables"])

    # check if all statblocks and images were used
    unused_statblocks = [v for _, v in access_tracking_statblocks.get_unused().items()]
    unused_images = []
    for _, images in access_tracking_images.get_unused().items():
        unused_images.extend(images)
    if len(unused_statblocks) > 0 or len(unused_images) > 0:
        raise ValueError("Unused statlbocks and/or images")

    # render the entire pamphlet
    pamphlet_context: dict = dict(lore_html=lore_html_raw)
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
