from functools import partial

from jinja2 import Environment, PackageLoader, select_autoescape

from .utilities import (
    branding,
    columns,
    fix_punctuation,
    markdown_no_wrapping_p,
    matching_css_link,
    matching_js_link,
    sluggify,
)


def setup_jinja_env(env: Environment):
    env.filters["fix_punctuation"] = fix_punctuation
    env.filters["sluggify"] = sluggify
    env.filters["markdown_no_wrapping_p"] = markdown_no_wrapping_p
    env.filters["matching_css_link"] = matching_css_link
    env.filters["matching_js_link"] = matching_js_link
    env.globals["columns"] = columns
    env.globals["branding"] = partial(branding, env)


JinjaEnv = Environment(
    loader=PackageLoader("foe_foundry_data", package_path="jinja"),
    autoescape=select_autoescape(),
    extensions=["jinja_markdown.MarkdownExtension"],
)
setup_jinja_env(JinjaEnv)
