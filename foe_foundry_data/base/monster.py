from __future__ import annotations

from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass(kw_only=True)
class MonsterInfoModel:
    """Basic information about a monster"""

    key: str
    name: str
    cr: float
    template: str
    background_image: str | None = None
    creature_type: str | None = None
    tag_line: str | None = None


@dataclass(kw_only=True)
class MonsterTemplateInfoModel:
    """Basic information about a monster template"""

    key: str
    name: str
    url: str
    image: str
    tagline: str
    transparent_edges: bool
    grayscale: bool
    background_color: str | None
    mask_css: str
    is_new: bool
    create_date: datetime
