from pydantic.dataclasses import dataclass

from ..base import MonsterInfoModel


@dataclass(kw_only=True)
class MonsterFamilyModel:
    """Information about a family of similar monsters"""

    key: str
    name: str
    tag_line: str
    monsters: list[MonsterInfoModel]
