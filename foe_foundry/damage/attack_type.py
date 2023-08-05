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

    def is_spell(self) -> bool:
        return self in {AttackType.RangedSpell}

    def is_mundane(self) -> bool:
        return not self.is_spell()

    def is_weapon(self) -> bool:
        return self in {AttackType.MeleeWeapon, AttackType.RangedWeapon}
