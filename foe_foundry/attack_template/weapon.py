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
            supports_secondary_damage_type=True,
        )


class _SpearAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spear",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            allows_shield=True,
            die=Die.d8,
            supports_secondary_damage_type=True,
        )


class _MaceAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Mace",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d8,
            supports_secondary_damage_type=True,
        )


class _RapierAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Rapier",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            allows_shield=True,
            die=Die.d8,
            supports_secondary_damage_type=True,
        )


class _Maul(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Maul",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d12,
            supports_secondary_damage_type=True,
        )


class _Greatsword(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greatsword",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d6,
            supports_secondary_damage_type=True,
        )


class _Polearm(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Polearm",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d10,
            supports_secondary_damage_type=True,
        )


class _Greataxe(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greataxe",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d12,
            supports_secondary_damage_type=True,
        )


class _Daggers(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Daggers",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d4,
            supports_secondary_damage_type=True,
        )


class _Longbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Longbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d8,
            supports_secondary_damage_type=True,
        )


class _Shortbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Shortbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            supports_secondary_damage_type=True,
        )


class _Crossbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Crossbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            supports_secondary_damage_type=True,
        )


class _Traps(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Traps",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d4,
            supports_secondary_damage_type=True,
        )


Crossbow: AttackTemplate = _Crossbow()
Daggers: AttackTemplate = _Daggers()
Greatsword: AttackTemplate = _Greatsword()
Greataxe: AttackTemplate = _Greataxe()
Longbow: AttackTemplate = _Longbow()
MaceAndShield: AttackTemplate = _MaceAndShield()
Maul: AttackTemplate = _Maul()
Polearm: AttackTemplate = _Polearm()
RapierAndShield: AttackTemplate = _RapierAndShield()
Shortbow: AttackTemplate = _Shortbow()
SpearAndShield: AttackTemplate = _SpearAndShield()
SwordAndShield: AttackTemplate = _SwordAndShield()
Traps: AttackTemplate = _Traps()
