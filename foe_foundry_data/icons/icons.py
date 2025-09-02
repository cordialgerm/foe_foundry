import hashlib
import io
import re
import shutil
from functools import cached_property
from pathlib import Path

import cairosvg
from bs4 import BeautifulSoup
from markupsafe import Markup
from PIL import Image, ImageColor, ImageDraw, ImageFont


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


def _hash_og_image_params(
    icon: str,
    title: str,
    background_texture: str,
    background_texture_opacity: float,
    background_color: str,
    foreground_color: str,
) -> str:
    """Generate a hash from the input parameters for og_image_for_icon caching."""
    hasher = hashlib.md5()

    # Hash all the parameters that affect the output
    params = f"{icon}|{title}|{background_texture}|{background_texture_opacity}|{background_color}|{foreground_color}"
    hasher.update(params.encode("utf-8"))

    return hasher.hexdigest()


def og_image_for_icon(
    icon: str,
    title: str,
    output_path: Path,
    background_texture: str = "img/backgrounds/parchment-stained.png",
    background_texture_opacity: float = 0.2,
    background_color: str = "#2a2a2a",
    foreground_color: str = "#ff3737",
    allow_cache: bool = True,
) -> Path:
    """Generates an Open Graph image with a solid color, a semi-transparent background image, and an SVG icon with title."""

    # Set up cache directory
    cache_dir = Path.cwd() / "cache" / "og_image_for_icon"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate hash for caching
    cache_hash = _hash_og_image_params(
        icon,
        title,
        background_texture,
        background_texture_opacity,
        background_color,
        foreground_color,
    )
    cached_path = cache_dir / f"{cache_hash}.png"

    # Check if cached version exists
    if allow_cache and cached_path.exists():
        # Copy cached image to output path
        shutil.copy2(cached_path, output_path)
        return output_path

    # Constants
    OG_WIDTH, OG_HEIGHT = 1200, 630
    ICON_SIZE = 400
    ICON_PADDING_TOP = 80
    TEXT_PADDING_TOP = ICON_PADDING_TOP + ICON_SIZE + 40
    FONT_SIZE = 60

    docs_dir = Path(__file__).parent.parent.parent / "docs"
    font_dir = docs_dir / "fonts"
    font_path = font_dir / "UncialAntiqua-Regular.ttf"

    # Create solid color background
    base = Image.new("RGBA", (OG_WIDTH, OG_HEIGHT), background_color)

    # Load and resize background image
    background_path = docs_dir / background_texture

    bg_img = Image.open(background_path).convert("RGBA")
    bg_img = bg_img.resize((OG_WIDTH, OG_HEIGHT))

    # Set background image opacity
    alpha = int(255 * background_texture_opacity)
    bg_img.putalpha(alpha)

    # Composite background image over solid color
    base = Image.alpha_composite(base, bg_img)

    # Render SVG to PNG in memory
    svg_string = str(icon_svg(icon, fill=foreground_color))
    png_data = cairosvg.svg2png(
        bytestring=svg_string, output_width=ICON_SIZE, output_height=ICON_SIZE
    )
    png_bytes = io.BytesIO(png_data)  # type: ignore
    icon_image = Image.open(png_bytes).convert("RGBA")

    # Composite icon onto background
    icon_x = (OG_WIDTH - ICON_SIZE) // 2
    icon_y = ICON_PADDING_TOP
    base.paste(icon_image, (icon_x, icon_y), icon_image)

    # Draw text
    draw = ImageDraw.Draw(base)
    try:
        font = ImageFont.truetype(font_path, FONT_SIZE)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_x = (OG_WIDTH - text_width) // 2
    text_y = TEXT_PADDING_TOP

    # Draw text shadow (background color, but fully opaque) slightly offset in several directions

    try:
        shadow_rgba = ImageColor.getrgb(background_color) + (180,)
    except Exception:
        # fallback to dark gray if color parsing fails
        shadow_rgba = (42, 42, 42, 255)
    shadow_offsets = [
        (-2, -2),
        (2, -2),
        (-2, 2),
        (2, 2),
        (0, 2),
        (0, -2),
        (2, 0),
        (-2, 0),
    ]
    for dx, dy in shadow_offsets:
        draw.text((text_x + dx, text_y + dy), title, fill=shadow_rgba, font=font)

    # Draw main text
    draw.text((text_x, text_y), title, fill=foreground_color, font=font)

    # Save the final image
    rgb_base = base.convert("RGB")
    rgb_base.save(output_path, format="PNG")

    # Save a copy to cache for future use
    rgb_base.save(cached_path, format="PNG")

    return output_path
