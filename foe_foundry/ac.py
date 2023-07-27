from __future__ import annotations

from dataclasses import dataclass

from .creature_types import CreatureType
from .role_types import MonsterRole


@dataclass
class ArmorClass:
    value: int
    description: str | None = None

    def delta(self, val: int) -> ArmorClass:
        return ArmorClass(value=self.value + val, description=self.description)

    def describe(self) -> str:
        t = f"{self.value}"
        if self.description is not None:
            t += f" ({self.description})"
        return t


def flavorful_ac(ac: int, creature_type: CreatureType, role: MonsterRole) -> ArmorClass:
    if creature_type in {
        CreatureType.Beast,
        CreatureType.Monstrosity,
        CreatureType.Ooze,
        CreatureType.Dragon,
        CreatureType.Elemental,
    }:
        return ArmorClass(value=ac, description="natural armor")

    elif role == MonsterRole.Defender:
        # heavy armor
        if ac <= 12:
            description = "shield"
        elif ac <= 14:
            description = "ring mail"
        elif ac <= 15:
            description = "ring mail, shield"
        elif ac <= 17:
            description = "chain mail, shield"
        elif ac <= 19:
            description = "splint mail, shield"
        else:
            description = "plate mail, shield"
    else:
        if ac <= 10:
            description = "unarmored"
        elif ac <= 12:
            description = "hide"
        elif ac <= 14:
            description = "chain shirt"
        elif ac <= 15:
            description = "scale mail"
        elif ac <= 16:
            description = "breastplate"
        else:
            description = "breastplate, shield"

    return ArmorClass(value=ac, description=description)
