import base64
from io import BytesIO
from pathlib import Path
from typing import Any

from jinja2 import Environment
from markdown import markdown
from markupsafe import Markup
from PIL import Image


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


def resize_image_as_base64_png(path: Path, max_size: int = 300) -> str:
    """
    Resize an image to fit within a square of max_size pixels and convert it to a base64-encoded PNG string.
    """

    img = Image.open(path)
    if img.height >= img.width and img.height > max_size:
        new_width = int(1.0 * max_size / img.height * img.width)
        img.thumbnail((new_width, max_size))
    elif img.width >= img.height and img.width > max_size:
        new_height = int(1.0 * max_size / img.width * img.height)
        img.thumbnail((max_size, new_height))

    io = BytesIO()
    img.save(io, format="png")
    io.seek(0)
    bytes_data = io.read()
    base64_bytes = base64.b64encode(bytes_data)
    base64_str = base64_bytes.decode("utf-8")
    return base64_str


def statblock(env: Environment, statblock: dict, break_after: bool = True) -> Markup:
    template = env.get_template("statblock.html.j2")
    html = "<div>" + template.render(statblock=statblock) + "</div>"
    if break_after:
        html += '\n<div class="break-after"></div>'

    return Markup(html)  # Mark as safe to avoid escaping


def image(name: str, alt: str, mode: str = "foreground", **kwargs) -> Markup:
    """
    Returns an HTML image tag with the specified name and mode (foreground or background).
    The image is resized to fit within a square of 300 pixels and converted to a base64-encoded PNG string.
    """
    monster_dir = (
        Path(__file__).parent.parent.parent.parent
        / "foe_foundry_ui"
        / "public"
        / "img"
        / "monster2"
    )
    img_path = monster_dir / name
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    base64_str = resize_image_as_base64_png(img_path)

    if mode == "foreground":
        img_class = "monster-image foreground"
    elif mode == "background":
        img_class = "monster-image background"
    else:
        raise ValueError(f"Invalid mode: {mode}")

    if "class" in kwargs:
        img_class = f"{img_class} {kwargs['class']}"
        kwargs.pop("class")

    attrs = element_attributes(
        {
            "class": img_class,
            "alt": alt,
            "src": f"data:image/png;base64, {base64_str}",
        }
        | kwargs
    )

    img_html = f"<img {attrs} />"
    return Markup(img_html)


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
