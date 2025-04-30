from __future__ import annotations

from enum import auto
from typing import List, Set, cast

from backports.strenum import StrEnum


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

    @staticmethod
    def Primal() -> Set[DamageType]:
        return {
            DamageType.Fire,
            DamageType.Cold,
            DamageType.Lightning,
            DamageType.Thunder,
        }

    @property
    def is_physical(self) -> bool:
        return self in {
            DamageType.Bludgeoning,
            DamageType.Piercing,
            DamageType.Slashing,
        }

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

    @property
    def adj(self) -> str:
        if self == DamageType.Acid:
            return "acidic"
        elif self == DamageType.Bludgeoning:
            return "bludgeoning"
        elif self == DamageType.Cold:
            return "freezing"
        elif self == DamageType.Fire:
            return "fiery"
        elif self == DamageType.Force:
            return "energetic"
        elif self == DamageType.Lightning:
            return "shocking"
        elif self == DamageType.Necrotic:
            return "deathly"
        elif self == DamageType.Piercing:
            return "piercing"
        elif self == DamageType.Poison:
            return "poisonous"
        elif self == DamageType.Psychic:
            return "mind-shattering"
        elif self == DamageType.Radiant:
            return "holy"
        elif self == DamageType.Slashing:
            return "slashing"
        elif self == DamageType.Thunder:
            return "thunderous"
        else:
            raise ValueError(f"Unknown damage type {self}")
