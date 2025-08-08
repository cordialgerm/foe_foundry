from __future__ import annotations

from pydantic.dataclasses import dataclass


@dataclass(kw_only=True)
class MonsterInfoModel:
    """Basic information about a monster"""

    key: str
    name: str
    cr: float
    template: str
