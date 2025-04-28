from functools import partial

from jinja2 import Template

from .utilities import (
    branding,
    columns,
    fix_punctuation,
    image,
    jinja_env,
    markdown_no_wrapping_p,
    statblock,
)

JinjaEnv = jinja_env()
JinjaEnv.filters["fix_punctuation"] = fix_punctuation
JinjaEnv.filters["markdown_no_wrapping_p"] = markdown_no_wrapping_p
JinjaEnv.globals["statblock"] = partial(statblock, JinjaEnv)
JinjaEnv.globals["columns"] = columns
JinjaEnv.globals["image"] = image
JinjaEnv.globals["branding"] = partial(branding, JinjaEnv)


def load_template_from_markdown(md_template_str: str) -> Template:
    """Loads a jinja template from a markdown content"""
    template = JinjaEnv.from_string(md_template_str)
    return template
