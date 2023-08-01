from ..creature_types import CreatureType
from ..damage import AttackType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_ac_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, ac_modifier=-2)
    return _as_artillery(stats, dials)


def as_low_hp_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, hp_multiplier=0.8)
    return _as_artillery(stats, dials)


def as_low_ac_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=1, attack_damage_dice_modifier=1, ac_modifier=-2)
    return _as_artillery(stats, dials)


def as_low_hp_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        attack_hit_modifier=1, attack_damage_dice_modifier=1, hp_multiplier=0.8
    )
    return _as_artillery(stats, dials)


def _as_artillery(stats: BaseStatblock, dials: MonsterDials) -> BaseStatblock:
    new_attack_type = (
        AttackType.RangedWeapon
        if stats.creature_type == CreatureType.Humanoid
        else AttackType.RangedSpell
    )

    changes: dict = dict(role=MonsterRole.Artillery, attack_type=new_attack_type)

    if new_attack_type == AttackType.RangedSpell and stats.secondary_damage_type is not None:
        # if the monster has a secondary damage type, then prefer that for the ranged spell damage
        changes.update(primary_damage_type=stats.secondary_damage_type)

    return stats.apply_monster_dials(dials).copy(**changes)


ArtilleryLowAcMaxDmg = role_variant(
    "Artillery.LowAcMaxDmg", MonsterRole.Artillery, as_low_ac_artillery_max_dmg
)
ArtilleryLowHpMaxDmg = role_variant(
    "Artillery.LowHpMaxDmg", MonsterRole.Artillery, as_low_hp_artillery_max_dmg
)
ArtilleryLowAcBalanced = role_variant(
    "Artillery.LowAcBalanced", MonsterRole.Artillery, as_low_ac_artillery_balanced
)
ArtilleryLowHpBalanced = role_variant(
    "Artillery.LowHpBalanced", MonsterRole.Artillery, as_low_hp_artillery_balanced
)
Artillery = RoleTemplate(
    "Artillery",
    MonsterRole.Artillery,
    [
        ArtilleryLowAcMaxDmg,
        ArtilleryLowHpMaxDmg,
        ArtilleryLowAcBalanced,
        ArtilleryLowHpBalanced,
    ],
)
