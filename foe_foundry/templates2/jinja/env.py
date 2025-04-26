from functools import partial

from jinja2 import Environment, PackageLoader, select_autoescape

from .monster_ref import TestMonsterRefResolver
from .utilities import (
    columns,
    fix_punctuation,
    image,
    markdown_no_wrapping_p,
    statblock,
    statblock_ref,
)

ref_resolver = TestMonsterRefResolver()

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
JinjaEnv.globals["statblock_ref"] = partial(statblock_ref, JinjaEnv, ref_resolver)
