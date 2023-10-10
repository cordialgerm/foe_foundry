from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate


class _SwordAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Longsword",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            allows_shield=True,
            die=Die.d8,
        )


class _SpearAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spear",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            allows_shield=True,
            die=Die.d8,
        )


class _MaceAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Mace",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d8,
        )


class _Maul(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Maul",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d12,
        )


class _Greatsword(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greatsword",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d6,
        )


class _Polearm(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Polearm",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d10,
        )


class _Greataxe(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greataxe",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d12,
        )


class _Daggers(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Daggers",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d4,
        )


class _Longbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Longbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d8,
        )


class _Shortbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Shortbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d6,
        )


class _Crossbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Crossbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
        )


Longbow: AttackTemplate = _Longbow()
Shortbow: AttackTemplate = _Shortbow()
Crossbow: AttackTemplate = _Crossbow()
SwordAndShield: AttackTemplate = _SwordAndShield()
SpearAndShield: AttackTemplate = _SpearAndShield()
MaceAndShield: AttackTemplate = _MaceAndShield()
Maul: AttackTemplate = _Maul()
Greatsword: AttackTemplate = _Greatsword()
Polearm: AttackTemplate = _Polearm()
Greataxe: AttackTemplate = _Greataxe()
Daggers: AttackTemplate = _Daggers()
