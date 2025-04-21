from io import BytesIO  # noqa
from pathlib import Path
from typing import List
import base64
import pdfkit
from markdown import markdown
from markupsafe import Markup
from functools import partial

import numpy as np
from jinja2 import Environment, PackageLoader, select_autoescape
from PIL import Image  # noqa

from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
)

from ..benchmarks import Benchmark
from ..statblocks import Statblock
from .data import MonsterTemplateData
from .utilities import fix_punctuation


def render_statblock(env, statblock, break_after: bool = True):
    template = env.get_template("creature_template.html.j2")
    html = "<div>" + template.render(statblock=statblock) + "</div>"
    if break_after:
        html += '\n<div class="break-before"></div>'

    return Markup(html)  # Mark as safe to avoid escaping


def render_images(images):
    pieces = []
    for img in images:
        pieces.append(
            f"<img src='data:image/{img['image_ext']};base64, {img['image_base64']}' />"
        )
    html = "\n".join(pieces)
    return Markup(html)


env = Environment(
    loader=PackageLoader("foe_foundry"),
    autoescape=select_autoescape(),
    extensions=["jinja_markdown.MarkdownExtension"],
)
env.filters["fix_punctuation"] = fix_punctuation
env.globals["render_statblock"] = partial(render_statblock, env)
env.globals["render_images"] = render_images


def render_html_to_path(stats: Statblock, path: Path) -> Path:
    template = env.get_template("creature_template.html.j2")
    data = MonsterTemplateData.from_statblock(stats)
    html_raw = template.render(dict(statblock=data.to_dict()))

    with path.open("w") as f:
        f.write(html_raw)

    return path


def render_html_inline(
    stats: Statblock, benchmarks: List[Benchmark] | None = None
) -> str:
    template = env.get_template("inlined_template.html.j2")
    data = MonsterTemplateData.from_statblock(stats, benchmarks)
    html_raw = template.render(name=data.name, statblock=data.to_dict())
    return html_raw


def render_html_fragment(
    stats: Statblock, benchmarks: List[Benchmark] | None = None
) -> str:
    template = env.get_template("creature_template.html.j2")
    data = MonsterTemplateData.from_statblock(stats, benchmarks)
    html_raw = template.render(dict(statblock=data.to_dict()))
    return html_raw


def render_html_inline_page_to_path(
    stats: Statblock, path: Path, benchmarks: List[Benchmark] | None = None
) -> Path:
    html_raw = render_html_inline(stats, benchmarks)

    with path.open("w") as f:
        f.write(html_raw)

    return path


class AccessTrackingDict(dict):
    """Keep track of which keys have been accessed so we know if statblocks have been used"""

    def __init__(self, **kwargs):
        new_kwargs = {k.replace("_", "-"): v for k, v in kwargs.items()}

        super().__init__(**new_kwargs)
        self.accessed_keys = set()

    def __getitem__(self, key):
        key = key.lower().replace("_", "-")
        self.accessed_keys.add(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = key.lower().replace("_", "-")
        super().__setitem__(key, value)

    def get_unused_keys(self):
        return set(self.keys()) - self.accessed_keys

    def get_unused(self) -> dict:
        unused = {}
        for unused_key in self.get_unused_keys():
            unused[unused_key] = super().__getitem__(unused_key)
        return unused


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

    # track which statblocks get used by Jinja so we know if we need to render defaults
    access_tracking_statblocks = AccessTrackingDict(**statblocks)

    # load images for each statblock
    images: dict[str, list[dict]] = {}
    for variant_key, image_paths in template.image_urls.items():
        variant_images = []
        for image_path in image_paths:
            base64_str = _resize_image_as_base64_png(image_path)
            variant_images.append(dict(image_ext="png", image_base64=base64_str))
        images[variant_key] = variant_images

    access_tracking_images = AccessTrackingDict(**images)

    # get lore template
    lore_template_str = template.lore_md.strip()
    if len(lore_template_str) == 0:
        lore_template_str = f"# {template.name}\n\nNo Lore Available"

    lore_template = env.from_string(lore_template_str)

    lore_context: dict = dict(
        statblocks=access_tracking_statblocks, images=access_tracking_images
    )

    lore_md_raw = lore_template.render(lore_context)
    lore_html_raw = markdown(lore_md_raw, extensions=["tables"])

    unused_statblocks = [v for _, v in access_tracking_statblocks.get_unused().items()]
    unused_images = []
    for _, images in access_tracking_images.get_unused().items():
        unused_images.extend(images)

    template_context: dict = dict(
        lore_html=lore_html_raw,
        unused_statblocks=unused_statblocks,
        unused_images=unused_images,
    )

    jinja_template = env.get_template("pamphlet_template.html.j2")
    html_raw = jinja_template.render(template_context)

    with path.open("w") as f:
        f.write(html_raw)

    return path


def _render_pdf(path: Path) -> Path:
    new_path = path.with_suffix(".pdf")
    pdfkit.from_file(str(path), output_path=str(new_path))
    return new_path


def _resize_image_as_base64_png(path: Path, max_size: int = 300) -> str:
    img = Image.open(path)
    if img.height >= img.width and img.height > max_size:
        new_width = int(1.0 * max_size / img.height * img.width)
        img.thumbnail((new_width, max_size))
    elif img.width >= img.height and img.width > max_size:
        new_height = int(1.0 * max_size / img.width * img.height)
        img.thumbnail((max_size, new_height))

    io = BytesIO()
    img.save(io, format="png")
    io.seek(0)
    bytes_data = io.read()
    base64_bytes = base64.b64encode(bytes_data)
    base64_str = base64_bytes.decode("utf-8")
    return base64_str
