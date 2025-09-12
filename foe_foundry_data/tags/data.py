"""Tag data models for API responses."""

from __future__ import annotations

from typing import List

from pydantic.dataclasses import dataclass

from ..base import MonsterInfoModel


@dataclass(kw_only=True)
class TagInfoModel:
    """Comprehensive tag information for API responses"""

    key: str
    name: str
    description: str
    icon: str
    color: str
    category: str

    # Example monsters using this tag (prioritized for diversity)
    example_monsters: List[MonsterInfoModel]

    @staticmethod
    def from_tag_definition(
        tag_def, example_monsters: List[MonsterInfoModel]
    ) -> "TagInfoModel":
        """Create TagInfoModel from TagDefinition with example monsters"""
        return TagInfoModel(
            key=tag_def.key,
            name=tag_def.name,
            description=tag_def.description,
            icon=tag_def.icon,
            color=tag_def.color,
            category=tag_def.category,
            example_monsters=example_monsters,
        )
