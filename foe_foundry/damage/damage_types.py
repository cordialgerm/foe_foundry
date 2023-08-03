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
