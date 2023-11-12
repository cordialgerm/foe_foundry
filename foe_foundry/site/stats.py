from __future__ import annotations

from dataclasses import fields
from typing import List, Optional, Set

from pydantic.dataclasses import dataclass

from ..ac import ResolvedArmorClass
from ..attributes import Attributes
from ..creature_types import CreatureType
from ..damage import Attack, AttackType, Condition, DamageType
from ..die import DieFormula
from ..features import Feature
from ..movement import Movement
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size


@dataclass(kw_only=True)
class StatblockModel:
    name: str
    cr: float
    hp: DieFormula
    speed: Movement
    ac: ResolvedArmorClass
    uses_shield: bool
    attributes: Attributes
    attack: Attack
    additional_attacks: List[Attack]
    features: List[Feature]
    multiattack: int
    size: Size
    creature_type: CreatureType
    creature_subtype: Optional[str]
    creature_class: Optional[str]
    languages: List[str]
    senses: Senses
    role: MonsterRole = MonsterRole.Default
    attack_type: AttackType = AttackType.MeleeWeapon
    damage_resistances: Set[DamageType]
    damage_immunities: Set[DamageType]
    condition_immunities: Set[Condition]
    nonmagical_resistance: bool
    nonmagical_immunity: bool

    @staticmethod
    def from_args(args: dict) -> StatblockModel:
        available = {f.name for f in fields(StatblockModel)}
        kwargs = {k: v for k, v in args.items() if k in available}
        missing = {a for a in available if a not in kwargs}
        for m in missing:
            kwargs[m] = None
        return StatblockModel(**kwargs)
