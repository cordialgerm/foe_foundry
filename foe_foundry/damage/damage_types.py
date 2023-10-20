from __future__ import annotations

from enum import StrEnum, auto
from typing import List, Set, cast

from ..die import Die


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

    @staticmethod
    def Elemental() -> Set[DamageType]:
        return {
            DamageType.Fire,
            DamageType.Cold,
            DamageType.Acid,
            DamageType.Lightning,
            DamageType.Poison,
        }

    @property
    def is_physical(self) -> bool:
        return self in {DamageType.Bludgeoning, DamageType.Piercing, DamageType.Slashing}

    @property
    def is_elemental(self) -> bool:
        return self in {
            DamageType.Acid,
            DamageType.Fire,
            DamageType.Cold,
            DamageType.Lightning,
            DamageType.Thunder,
            DamageType.Poison,
        }
