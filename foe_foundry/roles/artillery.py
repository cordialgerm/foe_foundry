from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_ac_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, ac_modifier=-2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Artillery, is_ranged=True)


def as_low_hp_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, hp_multiplier=0.8)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Artillery, is_ranged=True)


def as_low_ac_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=1, attack_damage_dice_modifier=1, ac_modifier=-2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Artillery, is_ranged=True)


def as_low_hp_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        attack_hit_modifier=1, attack_damage_dice_modifier=1, hp_multiplier=0.8
    )
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Artillery, is_ranged=True)


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
