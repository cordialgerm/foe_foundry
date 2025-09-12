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


def create_jinja_env():
    """Create Jinja environment with optional jinja_markdown extension"""
    extensions = []

    # Try to import and use jinja_markdown if available
    try:
        import jinja_markdown

        extensions.append("jinja_markdown.MarkdownExtension")
    except ImportError:
        # jinja_markdown is optional - continue without it
        pass

    return Environment(
        loader=PackageLoader("foe_foundry_data", package_path="jinja"),
        autoescape=select_autoescape(),
        extensions=extensions,
    )


JinjaEnv = create_jinja_env()
setup_jinja_env(JinjaEnv)
