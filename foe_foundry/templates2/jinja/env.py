from functools import partial

from jinja2 import Environment, PackageLoader, select_autoescape

from .utilities import (
    fix_punctuation,
    markdown_no_wrapping_p,
    render_images,
    render_statblock,
)

JinjaEnv = Environment(
    loader=PackageLoader("foe_foundry", package_path="templates2"),
    autoescape=select_autoescape(),
    extensions=["jinja_markdown.MarkdownExtension"],
)
JinjaEnv.filters["fix_punctuation"] = fix_punctuation
JinjaEnv.filters["markdown_no_wrapping_p"] = markdown_no_wrapping_p
JinjaEnv.globals["render_statblock"] = partial(render_statblock, JinjaEnv)
JinjaEnv.globals["render_images"] = render_images
