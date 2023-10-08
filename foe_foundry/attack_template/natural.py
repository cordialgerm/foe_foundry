from ..damage import AttackType, DamageType
from .template import AttackTemplate


class _Claw(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Claw",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Slashing,
        )


class _Bite(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Bite",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
        )


class _Horns(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Horns",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
        )


class _Stomp(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Stomp",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
        )


class _Tail(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Tail",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
        )


class _Slam(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Slam",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
        )


class _Tentacle(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Tentacle",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Bludgeoning,
        )


class _Stinger(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Stinger",
            attack_type=AttackType.MeleeNatural,
            damage_type=DamageType.Piercing,
        )


class _Spit(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spit",
            attack_type=AttackType.RangedNatural,
            damage_type=DamageType.Acid,
        )


class _Spines(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Spines",
            attack_type=AttackType.RangedNatural,
            damage_type=DamageType.Piercing,
        )


Claw: AttackTemplate = _Claw()
Bite: AttackTemplate = _Bite()
Horns: AttackTemplate = _Horns()
Stomp: AttackTemplate = _Stomp()
Slam: AttackTemplate = _Slam()
Tail: AttackTemplate = _Tail()
Spit: AttackTemplate = _Spit()
Spines: AttackTemplate = _Spines()
Stinger: AttackTemplate = _Stinger()
Tentacle: AttackTemplate = _Tentacle()
