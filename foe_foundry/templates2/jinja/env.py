from functools import partial

from jinja2 import Environment, PackageLoader, select_autoescape

from .utilities import (
    columns,
    fix_punctuation,
    image,
    markdown_no_wrapping_p,
    statblock,
)

JinjaEnv = Environment(
    loader=PackageLoader("foe_foundry", package_path="templates2"),
    autoescape=select_autoescape(),
    extensions=["jinja_markdown.MarkdownExtension"],
)
JinjaEnv.filters["fix_punctuation"] = fix_punctuation
JinjaEnv.filters["markdown_no_wrapping_p"] = markdown_no_wrapping_p
JinjaEnv.globals["statblock"] = partial(statblock, JinjaEnv)
JinjaEnv.globals["columns"] = columns
JinjaEnv.globals["image"] = image
