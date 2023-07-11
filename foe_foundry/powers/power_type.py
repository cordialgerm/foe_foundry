from enum import StrEnum, auto


class PowerType(StrEnum):
    Movement = auto()  # powers that modify movement and stealth
    Static = auto()  # powers that just modify static stats like attacks, defense, & skills
    Attack = auto()  # powers that modify the base attack action of the creature
    Common = auto()  # powers that aren't tied to a specific role or creature template
    Role = auto()  # powers that are tied to a specific role
    Creature = auto()  # powers that are tied to a specific creature template
