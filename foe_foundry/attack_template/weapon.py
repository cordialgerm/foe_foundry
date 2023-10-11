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
            split_secondary_damage=True,
        )


class _SpearAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spear",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            allows_shield=True,
            die=Die.d8,
            reach=10,
            split_secondary_damage=True,
        )


class _MaceAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Mace",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d8,
            split_secondary_damage=True,
        )


class _RapierAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Rapier",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            allows_shield=True,
            die=Die.d8,
            split_secondary_damage=True,
        )


class _Maul(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Maul",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            allows_shield=True,
            die=Die.d12,
            split_secondary_damage=True,
        )


class _Greatsword(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greatsword",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d6,
            split_secondary_damage=True,
        )


class _Polearm(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Polearm",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d10,
            reach=10,
            split_secondary_damage=True,
        )


class _Greataxe(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Greataxe",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d12,
            split_secondary_damage=True,
        )


class _Daggers(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Daggers",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d4,
            split_secondary_damage=True,
        )


class _Longbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Longbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d8,
            range=150,
            range_max=600,
            split_secondary_damage=True,
        )


class _Shortbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Shortbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            range=80,
            range_max=320,
            split_secondary_damage=True,
        )


class _Crossbow(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Crossbow",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            split_secondary_damage=True,
            die=Die.d10,
            range=100,
            range_max=400,
        )


class _Traps(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Traps",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d4,
            split_secondary_damage=True,
        )


class _Staff(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Staff",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Bludgeoning,
            die=Die.d6,
            split_secondary_damage=True,
        )


class _Whip(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Whip",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Slashing,
            die=Die.d4,
            range=15,
            range_max=30,
            range_bonus_for_high_cr=True,
            split_secondary_damage=True,
        )


class _JavelinAndShield(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Javelin",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            range=30,
            range_max=120,
            range_bonus_for_high_cr=True,
            split_secondary_damage=True,
            allows_shield=True,
        )


Crossbow: AttackTemplate = _Crossbow()
Daggers: AttackTemplate = _Daggers()
Greatsword: AttackTemplate = _Greatsword()
Greataxe: AttackTemplate = _Greataxe()
JavelinAndShield: AttackTemplate = _JavelinAndShield()
Longbow: AttackTemplate = _Longbow()
MaceAndShield: AttackTemplate = _MaceAndShield()
Maul: AttackTemplate = _Maul()
Polearm: AttackTemplate = _Polearm()
RapierAndShield: AttackTemplate = _RapierAndShield()
Shortbow: AttackTemplate = _Shortbow()
SpearAndShield: AttackTemplate = _SpearAndShield()
SwordAndShield: AttackTemplate = _SwordAndShield()
Staff: AttackTemplate = _Staff()
Traps: AttackTemplate = _Traps()
Whip: AttackTemplate = _Whip()
