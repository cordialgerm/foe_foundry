from enum import auto

from backports.strenum import StrEnum


class ActionType(StrEnum):
    Feature = auto()
    Action = auto()
    BonusAction = auto()
    Reaction = auto()
    Legendary = auto()
