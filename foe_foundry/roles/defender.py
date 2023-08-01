from ..role_types import MonsterRole
from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_high_ac_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-2,
    )
    return _as_defender(stats, dials)


def as_high_ac_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
    )
    return _as_defender(stats, dials)


def as_high_hp_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-2,
    )
    return _as_defender(stats, dials)


def as_high_hp_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
    )
    return _as_defender(stats, dials)


def _as_defender(stats: BaseStatblock, dials: MonsterDials):
    new_attributes = stats.attributes.grant_save_proficiency(*Stats.All()).boost(Stats.STR, 2)
    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Defender, attributes=new_attributes
    )


DefenderHighAcLowDamage = role_variant(
    "Defender.HighAcLowDmg", MonsterRole.Defender, as_high_ac_low_damage_defender
)
DefenderHighAcLowHit = role_variant(
    "Defender.HighAcLowHit", MonsterRole.Defender, as_high_ac_low_hit_defender
)
DefenderHighHpLowDamage = role_variant(
    "Defender.HighHpLowDamage", MonsterRole.Defender, as_high_hp_low_damage_defender
)
DefenderHighHpLowHit = role_variant(
    "Defender.HighHpLowHit", MonsterRole.Defender, as_high_hp_low_hit_defender
)
Defender = RoleTemplate(
    "Defender",
    MonsterRole.Defender,
    [
        DefenderHighAcLowDamage,
        DefenderHighAcLowHit,
        DefenderHighHpLowDamage,
        DefenderHighHpLowHit,
    ],
)
