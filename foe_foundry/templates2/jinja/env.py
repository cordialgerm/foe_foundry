from functools import partial

from jinja2 import Environment, PackageLoader, Template, select_autoescape

from .monster_ref import TestMonsterRefResolver
from .utilities import (
    branding,
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
JinjaEnv.globals["branding"] = partial(branding, JinjaEnv)


def load_template_from_markdown(md_template_str: str) -> Template:
    """Loads a jinja template from a markdown content"""
    template = JinjaEnv.from_string(md_template_str)
    return template
