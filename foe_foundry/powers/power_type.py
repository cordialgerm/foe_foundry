from enum import StrEnum, auto


class PowerType(StrEnum):
    Role = auto()  # powers that are tied to a specific role
    Creature = auto()  # powers that are tied to a specific creature template
    Theme = auto()  # powers that are related to a common theme
