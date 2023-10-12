from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate


class _Claw(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Claw",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Slashing,
            split_secondary_damage=True,
            reach_bonus_for_huge=True,
        )


class _Bite(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Bite",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
            split_secondary_damage=True,
        )


class _Horns(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Horns",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
            split_secondary_damage=True,
        )


class _Stomp(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Stomp",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
            split_secondary_damage=True,
        )


class _Tail(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Tail",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
            reach=10,
            reach_bonus_for_huge=True,
        )


class _Slam(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Slam",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
            split_secondary_damage=True,
        )


class _Tentacle(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Tentacle",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
            split_secondary_damage=True,
            reach=10,
            reach_bonus_for_huge=True,
        )


class _Stinger(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Stinger",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
            secondary_damage_type=DamageType.Poison,
            split_secondary_damage=True,
        )


class _Spit(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spit",
            attack_type=AttackType.RangedNatural,
            damage_type=DamageType.Acid,
            secondary_damage_type=DamageType.Acid,
            split_secondary_damage=True,
            range_bonus_for_high_cr=True,
        )


class _Spines(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spines",
            attack_type=AttackType.RangedNatural,
            damage_type=DamageType.Piercing,
            split_secondary_damage=True,
            range_bonus_for_high_cr=True,
        )


class _Lob(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Lob",
            attack_type=AttackType.RangedWeapon,
            damage_type=DamageType.Bludgeoning,
            die=Die.d10,
            range=60,
            range_max=240,
            range_bonus_for_high_cr=True,
            split_secondary_damage=False,
        )


class _Thrash(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Thrash",
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            reach_bonus_for_huge=True,
        )


Claw: AttackTemplate = _Claw()
Bite: AttackTemplate = _Bite()
Horns: AttackTemplate = _Horns()
Stomp: AttackTemplate = _Stomp()
Slam: AttackTemplate = _Slam()
Tail: AttackTemplate = _Tail()
Thrash: AttackTemplate = _Thrash()
Lob: AttackTemplate = _Lob()
Spit: AttackTemplate = _Spit()
Spines: AttackTemplate = _Spines()
Stinger: AttackTemplate = _Stinger()
Tentacle: AttackTemplate = _Tentacle()
