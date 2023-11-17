from __future__ import annotations

from dataclasses import fields
from typing import List, Optional, Set

from pydantic.dataclasses import dataclass

from foe_foundry import (
    Attack,
    AttackType,
    Attributes,
    Condition,
    CreatureType,
    DamageType,
    DieFormula,
    Feature,
    MonsterRole,
    Movement,
    ResolvedArmorClass,
    Senses,
    Size,
)


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
