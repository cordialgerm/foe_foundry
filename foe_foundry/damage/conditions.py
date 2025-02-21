from dataclasses import field
from enum import auto

from backports.strenum import StrEnum
from pydantic.dataclasses import dataclass

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
        full_description = f"{self.caption}. {self.description_3rd}"
        if self.immunity_clause != "":
            full_description += f" {self.immunity_clause}"
        self.full_description = full_description

    def __repr__(self) -> str:
        return self.full_description


def Burning(
    damage: DieFormula | str, damage_type: DamageType = DamageType.Fire
) -> CustomCondition:
    if isinstance(damage, DieFormula):
        damage = damage.description

    return CustomCondition(
        name="Burning",
        caption=f"**Burning** [{damage} {damage_type}]",
        description=f"At the start of each of your turns, you take {damage} {damage_type} damage. You or another creature within 5 feet of you can spend an action to end the condition.",
        description_3rd=f"A burning creature suffers {damage} ongoing {damage_type} damage at the start of each of its turns. A creature may use an action to end the condition.",
    )


def Bleeding(
    damage: DieFormula | str,
    damage_type: DamageType = DamageType.Piercing,
    dc: int = 10,
    threshold: int = 0,
) -> CustomCondition:
    if isinstance(damage, DieFormula):
        damage = damage.description

    if threshold > 0:
        healing = f"at least {threshold} points of magical healing"
    else:
        healing = "any magical healing"

    return CustomCondition(
        name="Bleeding",
        caption=f"**Bleeding** [{damage} {damage_type}]",
        description=f"You are bleeding and suffer {damage} ongoing {damage_type} at the end of each of your turns. \
            A creature may use an action to attempt a DC {dc} Medicine check to end the condition. \
            The condition also ends if you receive {healing}",
        description_3rd=f"A bleeding creature suffers {damage} ongoing {damage_type} damage at the end of each of its turns. \
            A creature may use an action to attempt a DC {dc} Medicine check to end the condition. \
            The condition also ends if the creature receives {healing}.",
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
        description="You are **Dazed** and drop whatever you are carrying.",
        description_3rd="A **Shocked** creature is **Dazed** and drops whatever it is carrying.",
    )


def Swallowed(
    damage: DieFormula | str,
    damage_type=DamageType.Acid,
    regurgitate_dc: int = 15,
    regurgitate_damage_threshold: int = 10,
) -> CustomCondition:
    if isinstance(damage, DieFormula):
        damage = damage.description

    return CustomCondition(
        name="Swallowed",
        caption="**Swallowed**",
        description=f"You are **Blinded**, **Restrained**, and have total cover against attacks and effects from the outside. You take {damage} ongoing {damage_type} damage at the start of each of your turns.  \
            If the creature that swallowed you takes {regurgitate_damage_threshold} damage or more on a single turn from a creature inside it, it must make a DC {regurgitate_dc} Constitution saving throw at the end of that turn or regurgitate all swallowed creatures which fall **Prone** in a space within 10 feet of it. \
            If the creature you are swallowed by dies, you are no longer restrained by it and can escape by using 15 feet of movement, exiting prone.",
        description_3rd=f"A swallowed creature is **Blinded**, **Restrained**, and has total cover against attacks and effects from the outside. It takes {damage} ongoing {damage_type} damage at the start of each of its turns.  \
            If the swallowing creature takes {regurgitate_damage_threshold} damage or more on a single turn from a creature inside it, it must make a DC {regurgitate_dc} Constitution saving throw at the end of that turn or regurgitate all swallowed creatures which fall **Prone** in a space within 10 feet of it. \
            If the swallowing creature dies, the swallowed creature is no longer restrained by it and can escape by using 15 feet of movement, exiting prone.",
    )


def Weakened(save_end_of_turn: bool = True) -> CustomCondition:
    return CustomCondition(
        name="Weakened",
        caption="**Weakened**"
        if not save_end_of_turn
        else "**Weakened** (save ends at end of turn)",
        immunity_clause="A creature that is immune to **Exhaustion** cannot be **Weakened**",
        description="You are severely weakened. Your attacks and spells deal half damage and you have disadvantage on Strength ability checks and saving throws.",
        description_3rd="A weakened creature deals half damage with its spells and attacks and has disadvantage on Strength ability checks and saving throws.",
    )


def Susceptible(damage_type: DamageType) -> CustomCondition:
    return CustomCondition(
        name=f"Susceptible to {damage_type.capitalize()}",
        caption=f"**Susceptible to {damage_type.capitalize()}**",
        description=f"You are susceptible to {damage_type}. While susceptible to {damage_type} you ignore any immunity or resistance to {damage_type} that you may have. If you had no such immunity, you are instead vulernable to {damage_type}.",
        description_3rd=f"A creature susceptible to {damage_type} ignores any immunity or resistance to {damage_type} that it may have. If it had no such immunity, it is instead vulnerable to {damage_type}.",
    )
