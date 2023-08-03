from enum import StrEnum, auto


class AttackType(StrEnum):
    MeleeWeapon = auto()
    MeleeNatural = auto()
    RangedWeapon = auto()
    RangedSpell = auto()

    def is_melee(self) -> bool:
        return self in {AttackType.MeleeNatural, AttackType.MeleeWeapon}

    def is_ranged(self) -> bool:
        return not self.is_melee()
