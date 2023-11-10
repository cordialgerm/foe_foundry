from enum import auto

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
