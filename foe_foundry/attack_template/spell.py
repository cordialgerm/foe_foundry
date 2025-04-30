from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate

Gaze = AttackTemplate(
    attack_name="Gaze",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Psychic,
    secondary_damage_type=DamageType.Psychic,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
    die=Die.d6,
)

Beam = AttackTemplate(
    attack_name="Beam",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Force,
    secondary_damage_type=DamageType.Force,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
    die=Die.d8,
)

ArcaneBurst = AttackTemplate(
    attack_name="Arcane Burst",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Force,
    secondary_damage_type=DamageType.Force,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
    die=Die.d10,
)

EldritchBlast = AttackTemplate(
    attack_name="Eldritch Blast",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Force,
    secondary_damage_type=DamageType.Force,
    die=Die.d10,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Firebolt = AttackTemplate(
    attack_name="Firebolt",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Fire,
    secondary_damage_type=DamageType.Fire,
    die=Die.d10,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Frostbolt = AttackTemplate(
    attack_name="Frostbolt",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Cold,
    secondary_damage_type=DamageType.Cold,
    die=Die.d8,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Acidsplash = AttackTemplate(
    attack_name="Acid Splash",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Acid,
    secondary_damage_type=DamageType.Acid,
    die=Die.d4,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Poisonbolt = AttackTemplate(
    attack_name="Poison Bolt",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Poison,
    secondary_damage_type=DamageType.Poison,
    die=Die.d6,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Shock = AttackTemplate(
    attack_name="Shock",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Lightning,
    secondary_damage_type=DamageType.Lightning,
    die=Die.d6,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Deathbolt = AttackTemplate(
    attack_name="Death Bolt",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Necrotic,
    secondary_damage_type=DamageType.Necrotic,
    die=Die.d6,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

HolyBolt = AttackTemplate(
    attack_name="Holy Bolt",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Radiant,
    secondary_damage_type=DamageType.Radiant,
    die=Die.d8,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)

Thundrousblast = AttackTemplate(
    attack_name="Thundrous Blast",
    attack_type=AttackType.RangedSpell,
    damage_type=DamageType.Thunder,
    secondary_damage_type=DamageType.Thunder,
    die=Die.d8,
    split_secondary_damage=False,
    range_bonus_for_high_cr=True,
)


def attack_template_for_damage(damage: DamageType) -> AttackTemplate:
    if damage == DamageType.Acid:
        return Acidsplash
    elif damage == DamageType.Fire:
        return Firebolt
    elif damage == DamageType.Force:
        return Beam
    elif damage == DamageType.Cold:
        return Frostbolt
    elif damage == DamageType.Psychic:
        return Gaze
    elif damage == DamageType.Radiant:
        return HolyBolt
    elif damage == DamageType.Poison:
        return Poisonbolt
    elif damage == DamageType.Lightning:
        return Shock
    elif damage == DamageType.Necrotic:
        return Deathbolt
    elif damage == DamageType.Thunder:
        return Thundrousblast
    else:
        raise ValueError(f"No spell attack type for {damage}")
