from __future__ import annotations

from enum import StrEnum, auto


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
        try:
            return MonsterRole[role.title()]
        except KeyError:
            raise ValueError(f"Unknown role: {role}")
