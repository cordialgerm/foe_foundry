from ..ac_templates import HeavyArmor, MediumArmor, NaturalArmor
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

    # defenders wear medium or heavy armor if possible, otherwise natural armor
    stats = stats.add_ac_templates([MediumArmor, HeavyArmor, NaturalArmor], uses_shield=True)

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
