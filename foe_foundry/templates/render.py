from pathlib import Path
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape

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
    html_raw = template.render(data.to_dict())

    with path.open("w") as f:
        f.write(html_raw)

    return path


def render_html_inline(stats: Statblock, benchmarks: List[Benchmark] | None = None) -> str:
    template = env.get_template("inlined_template.html.j2")
    data = MonsterTemplateData.from_statblock(stats, benchmarks)
    html_raw = template.render(data.to_dict())
    return html_raw


def render_html_inline_page_to_path(
    stats: Statblock, path: Path, benchmarks: List[Benchmark] | None = None
) -> Path:
    html_raw = render_html_inline(stats, benchmarks)

    with path.open("w") as f:
        f.write(html_raw)

    return path
