import io
import re
from functools import cached_property
from pathlib import Path

import cairosvg
from bs4 import BeautifulSoup
from markupsafe import Markup
from PIL import Image, ImageDraw, ImageFont


class _IconCache:
    @cached_property
    def icons(self) -> dict[str, Path]:
        return self.load_icons()

    def load_icons(self) -> dict[str, Path]:
        icons_dir = Path(__file__).parent.parent.parent / "docs" / "img" / "icons"
        icons = {}
        for icon in icons_dir.glob("*.svg"):
            icons[icon.name.lower()] = icon
        return icons


_icons = _IconCache()


def icon_path(icon: str) -> Path | None:
    """Returns the path to the icon file."""
    if not icon.endswith(".svg"):
        icon += ".svg"

    icon_path = _icons.icons.get(icon.lower())
    return icon_path


def icon_svg(icon: str, fill="") -> Markup | None:
    """Returns the icon as an SVG string with optional fill override."""
    path = icon_path(icon)
    if path is None:
        return None

    svg_raw = path.read_text(encoding="utf-8")

    # Remove all `fill="..."` or `fill='...'` attributes
    svg_cleaned = re.sub(r'\s*fill=["\'][^"\']*["\']', "", svg_raw)

    # If a fill color is specified, parse and modify the SVG
    if fill:
        soup = BeautifulSoup(svg_cleaned, "xml")
        svg_tag = soup.find("svg")
        if svg_tag:
            svg_tag["fill"] = fill  # type: ignore
            svg_cleaned = str(svg_tag)

    return Markup(svg_cleaned)


def inline_icon(icon: str, fill="", wrap: bool = True) -> Markup | None:
    """Returns the icon as an inline SVG with optional fill override."""

    svg_markup = icon_svg(icon, fill)
    if svg_markup is None:
        return None

    svg_cleaned = str(svg_markup)

    if wrap:
        return Markup(
            f'<span class="inline-icon" aria-hidden="true">{svg_cleaned}</span>'
        )
    else:
        return Markup(svg_cleaned)


def og_image_for_icon(
    background_path: Path, icon: str, title: str, output_path: Path
) -> Path:
    """Generates an Open Graph image based on an SVG Icon with the specified background and title."""

    # Constants
    OG_WIDTH, OG_HEIGHT = 1200, 630
    ICON_SIZE = 400
    ICON_PADDING_TOP = 80
    TEXT_PADDING_TOP = ICON_PADDING_TOP + ICON_SIZE + 40
    FONT_SIZE = 60
    FILL_COLOR = "#ff3737"

    docs_dir = Path(__file__).parent.parent.parent / "docs"

    font_dir = docs_dir / "fonts"
    font_path = font_dir / "UncialAntiqua-Regular.ttf"

    # Load and resize background
    background = Image.open(background_path).convert("RGBA")
    background = background.resize((OG_WIDTH, OG_HEIGHT))

    # Render SVG to PNG in memory
    svg_string = str(icon_svg(icon, fill=FILL_COLOR))
    png_data = cairosvg.svg2png(
        bytestring=svg_string, output_width=ICON_SIZE, output_height=ICON_SIZE
    )
    bytes = io.BytesIO(png_data)  # type: ignore
    icon_image = Image.open(bytes).convert("RGBA")

    # Composite icon onto background
    icon_x = (OG_WIDTH - ICON_SIZE) // 2
    icon_y = ICON_PADDING_TOP
    background.paste(icon_image, (icon_x, icon_y), icon_image)

    # Draw text
    draw = ImageDraw.Draw(background)
    try:
        font = ImageFont.truetype(font_path, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (OG_WIDTH - text_width) // 2
    text_y = TEXT_PADDING_TOP

    draw.text((text_x, text_y), title, fill=FILL_COLOR, font=font)

    # Save the final image
    background.save(output_path, format="PNG")

    return output_path
