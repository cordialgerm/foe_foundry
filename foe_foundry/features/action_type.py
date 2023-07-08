from enum import StrEnum, auto


class ActionType(StrEnum):
    Feature = auto()
    Action = auto()
    BonusAction = auto()
    Reaction = auto()
