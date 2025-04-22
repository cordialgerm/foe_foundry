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


def render_statblock(env: Environment, statblock: dict, break_after: bool = True):
    template = env.get_template("statblock.html.j2")
    html = "<div>" + template.render(statblock=statblock) + "</div>"
    if break_after:
        html += '\n<div class="break-after"></div>'

    return Markup(html)  # Mark as safe to avoid escaping


def render_images(images: list[dict]):
    pieces = []
    for img in images:
        pieces.append(
            f"<img class='monster-image' src='data:image/{img['image_ext']};base64, {img['image_base64']}' />"
        )
    html = "\n".join(pieces)
    return Markup(html)


def markdown_no_wrapping_p(md: str):
    html = markdown(text=md, extensions=["tables"])
    if html.startswith("<p>") and html.endswith("</p>"):
        html = html[3:-4]
    return Markup(html)  # Mark as safe to avoid escaping
