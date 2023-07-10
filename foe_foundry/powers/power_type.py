from enum import StrEnum, auto


class PowerType(StrEnum):
    Static = auto()  # powers that just modify static stats like attacks, defense, & skills
    Common = auto()  # powers that aren't tied to a specific role or creature template
    Role = auto()  # powers that are tied to a specific role
    Creature = auto()  # powers that are tied to a specific creature template
