from __future__ import annotations

from enum import StrEnum, auto
from typing import List, cast

from ..creature_types import CreatureType


class DamageType(StrEnum):
    Acid = auto()
    Bludgeoning = auto()
    Cold = auto()
    Fire = auto()
    Force = auto()
    Lightning = auto()
    Necrotic = auto()
    Piercing = auto()
    Poison = auto()
    Psychic = auto()
    Radiant = auto()
    Slashing = auto()
    Thunder = auto()

    @staticmethod
    def All() -> List[DamageType]:
        return [cast(DamageType, s) for s in DamageType._member_map_.values()]


def flavorful_damage_types(creature_type: CreatureType) -> List[DamageType] | None:
    if creature_type == CreatureType.Aberration:
        return [DamageType.Psychic]
    elif creature_type == CreatureType.Beast:
        return None
    elif creature_type == CreatureType.Celestial:
        return [DamageType.Radiant]
    elif creature_type == CreatureType.Construct:
        return [DamageType.Fire]
    elif creature_type == CreatureType.Dragon:
        return [
            DamageType.Fire,
            DamageType.Cold,
            DamageType.Acid,
            DamageType.Poison,
            DamageType.Lightning,
        ]
    elif creature_type == CreatureType.Elemental:
        return [DamageType.Fire, DamageType.Cold, DamageType.Lightning]
    elif creature_type == CreatureType.Fey:
        return None
    elif creature_type == CreatureType.Fiend:
        return [DamageType.Fire]
    elif creature_type == CreatureType.Giant:
        return [DamageType.Fire, DamageType.Cold]
    elif creature_type == CreatureType.Humanoid:
        return [DamageType.Poison]
    elif creature_type == CreatureType.Monstrosity:
        return [DamageType.Poison]
    elif creature_type == CreatureType.Undead:
        return [DamageType.Necrotic]
    elif creature_type == CreatureType.Ooze:
        return [DamageType.Acid]
    elif creature_type == CreatureType.Plant:
        return [DamageType.Poison]
