from pathlib import Path
from typing import Any

from jinja2 import Environment
from markdown import markdown
from markupsafe import Markup

from foe_foundry.utils import get_base_url, name_to_key


def fix_punctuation(text: Any) -> Any:
    """
    Fixes punctuation in a string by ensuring it ends with a period and removing unnecessary spaces before the period.
    """
    if not isinstance(text, str):
        return text

    text = text.strip()

    if text.endswith(".."):
        text = text[:-2] + "."

    if text.endswith(" ."):
        text = text[:-2] + "."

    if text.endswith(". ."):
        text = text[:-3] + "."

    if not text.endswith(".") and not text.endswith(">"):
        text = text + "."

    return text


def sluggify(value: str) -> str:
    return name_to_key(value)


def markdown_no_wrapping_p(md: str):
    """
    Converts markdown text to HTML without wrapping it in <p> tags.
    """
    html = markdown(text=md, extensions=["tables"])
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return Markup(html)  # Mark as safe to avoid escaping


def columns(start: bool = True) -> Markup:
    """
    Returns a div with two columns, one for the left and one for the right.
    """
    if start:
        return Markup('<div class="column-container">')
    else:
        return Markup("</div>")


def element_attributes(attributes: dict) -> str:
    """
    Converts a dictionary of attributes into a string of HTML attributes.
    """
    return (
        " ".join([f'{key}="{value}"' for key, value in attributes.items()])
        if attributes
        else ""
    )


def branding(
    env: Environment,
    icon_only: bool = False,
) -> Markup:
    """Returns the branding HTML markup."""
    macro_template = env.get_template("macros.html.j2")
    branding = macro_template.module.branding(icon_only=icon_only)  # type: ignore

    return Markup(branding)  # Mark as safe to avoid escaping


def matching_css_link(url: str) -> str:
    """Generates a link to the matching CSS file of a given URL."""

    if url == "/":
        url = "/homepage"

    slug = url.lower().strip("/").replace("/", "-")
    css_path = f"{slug}.css"
    full_path = Path.cwd() / "docs" / "css" / css_path
    if not full_path.exists():
        return f"<!-- No matching CSS file found for {url} -->"

    return f'<link href="{get_base_url()}/css/{css_path}" rel="stylesheet">'


def matching_js_link(url: str) -> str:
    """Generates a link to the matching JS file of a given URL."""

    if url == "/":
        url = "/homepage"

    slug = url.lower().strip("/").replace("/", "-")
    js_path = f"{slug}.js"
    full_path = Path.cwd() / "docs" / "scripts" / js_path
    if not full_path.exists():
        return f"<!-- No matching JS file found for {url} -->"

    return f'<script src="{get_base_url()}/scripts/{js_path}" defer></script>'
