from ..role_types import MonsterRole
from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant

defender_save_proficiencies = dict(proficient_saves=set(Stats.All()))


def as_high_ac_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-2,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_high_ac_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_high_hp_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-2,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_high_hp_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


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
