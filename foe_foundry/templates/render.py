from io import BytesIO  # noqa
from pathlib import Path
from typing import List
import base64
import pdfkit

import markdown
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

env = Environment(
    loader=PackageLoader("foe_foundry"),
    autoescape=select_autoescape(),
    extensions=["jinja_markdown.MarkdownExtension"],
)
env.filters["fix_punctuation"] = fix_punctuation


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


def render_pamphlet(template: CreatureTemplate, path: Path) -> Path:
    lore_md = template.lore_md.strip()
    if len(lore_md) == 0:
        lore_md = f"# {template.name}\n\nNo Lore Available"

    context: dict = dict(lore_html=markdown.markdown(lore_md, extensions=["tables"]))

    image_paths: set[Path] = set()
    for _, image in template.image_urls.items():
        image_paths.update(image)

    images = []
    for img_path in image_paths:
        base64_str = _resize_image_as_base64_png(img_path)
        images.append(dict(image_ext="png", image_base64=base64_str))

    context.update(images=images)

    def rng_factory():
        return np.random.default_rng()

    statblocks = []
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
            statblocks.append(MonsterTemplateData.from_statblock(stats))

    context.update(statblocks=statblocks)

    jinja_template = env.get_template("pamphlet_template.html.j2")
    html_raw = jinja_template.render(context)

    with path.open("w") as f:
        f.write(html_raw)

    # _render_pdf(path)

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
