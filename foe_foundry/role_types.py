from __future__ import annotations

from enum import auto
from typing import cast

from backports.strenum import StrEnum


class MonsterRole(StrEnum):
    Default = auto()
    Ambusher = auto()
    Artillery = auto()
    Bruiser = auto()
    Controller = auto()
    Defender = auto()
    Leader = auto()
    Skirmisher = auto()
    Support = auto()
    Soldier = auto()

    @staticmethod
    def parse(role: str) -> MonsterRole:
        return cast(MonsterRole, MonsterRole._member_map_[role.title()])
