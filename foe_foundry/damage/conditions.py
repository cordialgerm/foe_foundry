from dataclasses import dataclass, field
from enum import StrEnum, auto

from ..die.formula import DieFormula
from .damage_types import DamageType


class Condition(StrEnum):
    Blinded = auto()
    Charmed = auto()
    Deafened = auto()
    Exhaustion = auto()
    Frightened = auto()
    Grappled = auto()
    Incapacitated = auto()
    Invisible = auto()
    Paralyzed = auto()
    Petrified = auto()
    Poisoned = auto()
    Prone = auto()
    Restrained = auto()
    Stunned = auto()
    Unconscious = auto()


@dataclass
class CustomCondition:
    name: str
    caption: str
    description: str
    description_3rd: str
    immunity_clause: str = ""
    full_description: str = field(init=False)

    def __post_init__(self):
        self.full_description = f"{self.caption}. {self.description_3rd}"

    def __repr__(self) -> str:
        return self.full_description


def Burning(
    damage: DieFormula | str, damage_type: DamageType = DamageType.Fire
) -> CustomCondition:
    return CustomCondition(
        name="Burning",
        caption=f"**Burning** ({damage} {damage_type})",
        description=f"At the start of each of your turns, you take {damage} {damage_type} damage. You or another creature within 5 feet of you can spend an action to end the condition.",
        description_3rd=f"A burning creature suffers {damage} ongoing {damage_type} damage at the start of each of its turns. A creature may use an action to end the condition",
    )


def Frozen(dc: int) -> CustomCondition:
    return CustomCondition(
        name="Frozen",
        caption=f"**Frozen** (escape DC {dc})",
        immunity_clause="A creature that is immune to being **Restrained** cannot be **Frozen**",
        description=f"You are partially encased in ice. Your movement speed is zero, attacks made against you have advantage, and you are vulnerable to bludgeoning and thunder damage. \
            You or another creature can use an action to perform a DC {dc} Strength (Athletics) check to break the ice and end the condition. The condition also ends whenever you take any bludgeoning, thunder, or fire damage.",
        description_3rd=f"A **Frozen** creature is partially encased in ice. It has a movement speed of zero, attacks made against it are at advantage, and it is vulnerable to bludgeoning and thunder damage. \
            A creature may use an action to perform a DC {dc} Strength (Athletics) check to break the ice and end the condition. The condition also ends whenever the creature takes any bludgeoning, thunder, or fire damage.",
    )


def Dazed() -> CustomCondition:
    return CustomCondition(
        name="Dazed",
        caption="**Dazed**",
        immunity_clause="A creature that is immune to being **Stunned** cannot be **Dazed**",
        description="You can move or take an action on your tun, not both. You can't take bonus actions or free object interactions.",
        description_3rd="A **Dazed** creature can move or take an action on its turn, but not both. It cannot take bonus actions or free object interactions.",
    )


def Shocked() -> CustomCondition:
    return CustomCondition(
        name="Shocked",
        caption="**Shocked**",
        immunity_clause="A creature that is immune to being **Stunned** cannot be **Shocked**",
        description=f"You are **Dazed** and drop whatever you are carrying",
        description_3rd="A **Shocked** creature is **Dazed** and drops whatever it is carrying",
    )
