from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate

Claw: AttackTemplate = AttackTemplate(
    attack_name="Claw",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Slashing,
    split_secondary_damage=True,
    reach_bonus_for_huge=True,
    die=Die.d6,
    die_count=1,
)

Bite: AttackTemplate = AttackTemplate(
    attack_name="Bite",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    die=Die.d8,
    die_count=1,
)

Horns: AttackTemplate = AttackTemplate(
    attack_name="Horns",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    die=Die.d6,
    die_count=1,
)

Stomp: AttackTemplate = AttackTemplate(
    attack_name="Stomp",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Bludgeoning,
    split_secondary_damage=True,
    die=Die.d6,
    die_count=1,
)

Tail: AttackTemplate = AttackTemplate(
    attack_name="Tail",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Bludgeoning,
    reach=10,
    reach_bonus_for_huge=True,
    die=Die.d8,
    die_count=1,
)

Slam: AttackTemplate = AttackTemplate(
    attack_name="Slam",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Bludgeoning,
    split_secondary_damage=True,
    die=Die.d6,
    die_count=1,
)

Tentacle: AttackTemplate = AttackTemplate(
    attack_name="Tentacle",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Bludgeoning,
    split_secondary_damage=True,
    reach=10,
    reach_bonus_for_huge=True,
    die=Die.d6,
    die_count=1,
)

Stinger: AttackTemplate = AttackTemplate(
    attack_name="Stinger",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Piercing,
    secondary_damage_type=DamageType.Poison,
    split_secondary_damage=True,
    die=Die.d6,
    die_count=1,
)

Spit: AttackTemplate = AttackTemplate(
    attack_name="Spit",
    attack_type=AttackType.RangedNatural,
    damage_type=DamageType.Acid,
    secondary_damage_type=DamageType.Acid,
    split_secondary_damage=True,
    range_bonus_for_high_cr=True,
    die=Die.d4,
    die_count=1,
)

Spines: AttackTemplate = AttackTemplate(
    attack_name="Spines",
    attack_type=AttackType.RangedNatural,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    range_bonus_for_high_cr=True,
    die=Die.d6,
    die_count=1,
)

Lob: AttackTemplate = AttackTemplate(
    attack_name="Lob",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Bludgeoning,
    die=Die.d10,
    range=60,
    range_max=240,
    range_bonus_for_high_cr=True,
    split_secondary_damage=False,
    die_count=1,
)

Thrash: AttackTemplate = AttackTemplate(
    attack_name="Thrash",
    attack_type=AttackType.MeleeNatural,
    damage_type=DamageType.Piercing,
    die=Die.d6,
    die_count=1,
    reach_bonus_for_huge=True,
)
