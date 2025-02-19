from ..damage import AttackType, DamageType
from ..die import Die
from .template import AttackTemplate

SwordAndShield = AttackTemplate(
    attack_name="Longsword",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Slashing,
    allows_shield=True,
    die=Die.d8,
    die_count=1,
    split_secondary_damage=True,
)

SpearAndShield = AttackTemplate(
    attack_name="Spear",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Piercing,
    allows_shield=True,
    die=Die.d8,
    die_count=1,
    reach=10,
    split_secondary_damage=True,
)

MaceAndShield = AttackTemplate(
    attack_name="Mace",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Bludgeoning,
    allows_shield=True,
    die=Die.d8,
    die_count=1,
    split_secondary_damage=True,
)

RapierAndShield = AttackTemplate(
    attack_name="Rapier",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Piercing,
    allows_shield=True,
    die=Die.d8,
    die_count=1,
    split_secondary_damage=True,
)

Maul = AttackTemplate(
    attack_name="Maul",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Bludgeoning,
    allows_shield=False,
    die=Die.d12,
    die_count=1,
    split_secondary_damage=True,
)

Greatsword = AttackTemplate(
    attack_name="Greatsword",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Slashing,
    die=Die.d6,
    die_count=2,
    split_secondary_damage=True,
)

Polearm = AttackTemplate(
    attack_name="Polearm",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Slashing,
    die=Die.d10,
    reach=10,
    die_count=1,
    split_secondary_damage=True,
)

Greataxe = AttackTemplate(
    attack_name="Greataxe",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Slashing,
    die=Die.d12,
    die_count=1,
    split_secondary_damage=True,
)

Daggers = AttackTemplate(
    attack_name="Daggers",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Piercing,
    die=Die.d4,
    die_count=2,
    split_secondary_damage=True,
)

Longbow = AttackTemplate(
    attack_name="Longbow",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    die=Die.d8,
    die_count=1,
    range=150,
    range_max=600,
    split_secondary_damage=True,
)

Shortbow = AttackTemplate(
    attack_name="Shortbow",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    die=Die.d6,
    die_count=1,
    range=80,
    range_max=320,
    split_secondary_damage=True,
)

Crossbow = AttackTemplate(
    attack_name="Crossbow",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    die=Die.d10,
    die_count=1,
    range=100,
    range_max=400,
)

HandCrossbow = AttackTemplate(
    attack_name="Hand Crossbow",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    die=Die.d6,
    die_count=1,
    range=30,
    range_max=120,
)

Pistol = AttackTemplate(
    attack_name="Pistol",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    split_secondary_damage=True,
    die=Die.d10,
    die_count=1,
    range=30,
    range_max=90,
)

Traps = AttackTemplate(
    attack_name="Traps",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Piercing,
    die=Die.d4,
    die_count=2,
    split_secondary_damage=True,
)

Staff = AttackTemplate(
    attack_name="Staff",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Bludgeoning,
    die=Die.d6,
    die_count=1,
    split_secondary_damage=True,
)

Whip = AttackTemplate(
    attack_name="Whip",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Slashing,
    die=Die.d4,
    die_count=1,
    range=15,
    range_max=30,
    range_bonus_for_high_cr=True,
    split_secondary_damage=True,
)

JavelinAndShield = AttackTemplate(
    attack_name="Javelin",
    attack_type=AttackType.RangedWeapon,
    damage_type=DamageType.Piercing,
    die=Die.d6,
    die_count=1,
    range=30,
    range_max=120,
    range_bonus_for_high_cr=True,
    split_secondary_damage=True,
    allows_shield=True,
)

Shortswords = AttackTemplate(
    attack_name="Shortswords",
    attack_type=AttackType.MeleeWeapon,
    damage_type=DamageType.Slashing,
    die=Die.d6,
    die_count=2,
    split_secondary_damage=True,
    allows_shield=False,
)
