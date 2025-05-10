from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape
from markdown import markdown
from markupsafe import Markup


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


def jinja_env():
    return Environment(
        loader=PackageLoader("foe_foundry_data", package_path="jinja"),
        autoescape=select_autoescape(),
        extensions=["jinja_markdown.MarkdownExtension"],
    )
