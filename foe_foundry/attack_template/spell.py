from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate

## Spell

# Arcane Burst
# Eldritch Blast
# Gaze
# Beam


class _Gaze(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Gaze",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Psychic,
        )


class _Beam(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Beam",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Force,
        )


class _ArcaneBurst(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Arcane Burst",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Force,
        )


class _EldritchBlast(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Eldritch Blast",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Force,
            die=Die.d10,
        )


class _Firebolt(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Firebolt",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Fire,
            die=Die.d10,
        )


class _Frostbolt(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Frostbolt",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Cold,
            die=Die.d8,
        )


class _Acidsplash(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Acid Splash",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Acid,
            die=Die.d4,
        )


class _Poisonbolt(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Poison Bolt",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Poison,
            die=Die.d6,
        )


class _Shock(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Shock",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Lightning,
            die=Die.d6,
        )


class _Deathbolt(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Death Bolt",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Necrotic,
            die=Die.d6,
        )


class _Holybolt(AttackTemplate):
    def __init__(self):
        super().__init__(
            attack_name="Holy Bolt",
            attack_type=AttackType.RangedSpell,
            damage_type=DamageType.Radiant,
            die=Die.d6,
        )


ArcaneBurst: AttackTemplate = _ArcaneBurst()
Acidsplash: AttackTemplate = _Acidsplash()
Beam: AttackTemplate = _Beam()
Deathbolt: AttackTemplate = _Deathbolt()
EdlritchBlast: AttackTemplate = _EldritchBlast()
Firebolt: AttackTemplate = _Firebolt()
Frostbolt: AttackTemplate = _Frostbolt()
Gaze: AttackTemplate = _Gaze()
HolyBolt: AttackTemplate = _Holybolt()
Poisonbolt: AttackTemplate = _Poisonbolt()
Shock: AttackTemplate = _Shock()
