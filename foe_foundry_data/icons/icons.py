import re
from functools import cached_property
from pathlib import Path

from markupsafe import Markup


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


def inline_icon(icon: str) -> str | None:
    """Returns the icon as an inline SVG."""
    path = icon_path(icon)
    if path is None:
        return None

    svg_raw = path.read_text(encoding="utf-8")

    # Remove all `fill="..."` and `fill='...'` attributes so we can style the icon wtih CSS
    svg_cleaned = re.sub(r'\s*fill=["\'][^"\']*["\']', "", svg_raw)

    return Markup(f'<span class="inline-icon">{svg_cleaned}</span>')
