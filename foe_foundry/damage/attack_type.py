from __future__ import annotations

from enum import auto
from typing import Set

from backports.strenum import StrEnum


class AttackType(StrEnum):
    MeleeWeapon = auto()
    MeleeNatural = auto()
    RangedNatural = auto()
    RangedWeapon = auto()
    RangedSpell = auto()

    def is_melee(self) -> bool:
        return self in {AttackType.MeleeNatural, AttackType.MeleeWeapon}

    def is_ranged(self) -> bool:
        return not self.is_melee()

    def is_spell(self) -> bool:
        return self in {AttackType.RangedSpell}

    def is_mundane(self) -> bool:
        return not self.is_spell()

    def is_natural(self) -> bool:
        return self in {AttackType.MeleeNatural, AttackType.RangedNatural}

    def is_weapon(self) -> bool:
        return self in {AttackType.MeleeWeapon, AttackType.RangedWeapon}

    @staticmethod
    def All() -> Set[AttackType]:
        return {a for a in AttackType}

    @staticmethod
    def AllRanged() -> Set[AttackType]:
        return {a for a in AttackType if a.is_ranged()}

    @staticmethod
    def AllMelee() -> Set[AttackType]:
        return {a for a in AttackType if a.is_melee()}

    @staticmethod
    def AllSpell() -> Set[AttackType]:
        return {a for a in AttackType if a.is_spell()}

    @staticmethod
    def AllWeapon() -> Set[AttackType]:
        return {a for a in AttackType if a.is_weapon()}

    @staticmethod
    def AllNatural() -> Set[AttackType]:
        return {a for a in AttackType if a.is_natural()}
