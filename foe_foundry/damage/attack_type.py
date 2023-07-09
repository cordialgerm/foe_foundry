from enum import StrEnum, auto


class AttackType(StrEnum):
    MeleeWeapon = auto()
    MeleeNatural = auto()
    RangedWeapon = auto()
    RangedSpell = auto()
