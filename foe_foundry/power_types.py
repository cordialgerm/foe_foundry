from enum import auto

from backports.strenum import StrEnum


class PowerType(StrEnum):
    Attack = auto()  # A power that is primarily used to attack
    Defense = auto()  # A power that is primarily used to defend
    AreaOfEffect = auto()  # A power that affects a large area
    Movement = auto()  # A power that is used to move. can increase movement speed, teleport, or otherwise change the position of the user
    Debuff = auto()  # A power that weakens an opponent
    Buff = auto()  # A power that strengthens an ally
    Summon = auto()  # A power that brings a creature into existence
    Environmental = auto()  # A power that interacts with the environment
    Aura = auto()  # A power that creates a persistent effect around the user
    Healing = auto()  # A power that restores health to allies
    Utility = auto()  # A power that provides various non-combat benefits
    Magic = (
        auto()
    )  # A power that is magical in nature, such as spell casting or innate magic
    Stealth = (
        auto()
    )  # A power that allows for stealthy actions, such as hiding or sneaking
