from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic.dataclasses import dataclass


@dataclass(kw_only=True)
class MonsterTagInfo:
    """Tag information for display in UI"""

    tag: str  # Display name (e.g., "Tier 1")
    key: str  # API identifier (e.g., "tier_1")
    tag_type: str
    description: str
    icon: str
    color: str


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
    tags: List[MonsterTagInfo] | None = None


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


@dataclass(kw_only=True)
class MonsterFamilyInfo:
    """Information about a family of similar monsters"""

    key: str
    url: str
    name: str
    icon: str
    tag_line: str
    templates: list[MonsterTemplateInfoModel]
    monsters: list[MonsterInfoModel]
