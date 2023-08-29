from ..ac import ArmorClass
from ..role_types import MonsterRole
from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        attack_hit_modifier=-2,
    )
    return _as_defender(stats, dials)


def as_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
    )
    return _as_defender(stats, dials)


def _as_defender(stats: BaseStatblock, dials: MonsterDials):
    # defenders have save proficiencies
    new_attributes = stats.attributes.grant_save_proficiency(*Stats.All()).boost(Stats.STR, 2)
    stats = stats.copy(attributes=new_attributes)

    # defenders have high-quality armor and use shields if possible
    # this should result in a +3 to AC (+1 to armor, +2 from shield)
    new_ac = stats.ac.delta(
        change=1,
        shield_allowed=ArmorClass.could_use_shield_or_wear_armor(stats.creature_type),
        dex=stats.attributes.stat_mod(Stats.DEX),
        spellcasting=stats.attributes.spellcasting_mod,
    )
    stats = stats.copy(ac=new_ac)

    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


DefenderHighAcLowDamage = role_variant(
    "Defender.LowDmg", MonsterRole.Defender, as_low_hit_defender
)
DefenderHighAcLowHit = role_variant(
    "Defender.LowHit", MonsterRole.Defender, as_low_damage_defender
)

Defender = RoleTemplate(
    "Defender",
    MonsterRole.Defender,
    [
        DefenderHighAcLowDamage,
        DefenderHighAcLowHit,
    ],
)
