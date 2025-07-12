from enum import auto

from backports.strenum import StrEnum

# I already have a PowerType class in foe_foundry/powers/power_type.py
# what should I call this one instead?
# let's brainstorm some options:
# - PowerCategory
# - PowerClassification
# - PowerKind
# - PowerGroup
# - PowerTypeCategory
# - PowerTypeGroup
# - PowerTypeClassification
# - PowerTypeKind
# - PowerTypeClass


class PowerType(StrEnum):
    Attack = auto()  # A power that is primarily used to attack
    Defense = auto()  # A power that is primarily used to defend
    AreaOfEffect = auto()  # A power that affects a large area
    Movement = auto()  # A power that is used to move
    Debuff = auto()  # A power that weakens an opponent
    Buff = auto()  # A power that strengthens an ally
    Summon = auto()  # A power that brings a creature into existence
    Environmental = auto()  # A power that interacts with the environment
    Aura = auto()  # A power that creates a persistent effect around the user
    Healing = auto()  # A power that restores health to allies
    Utility = auto()  # A power that provides various non-combat benefits
