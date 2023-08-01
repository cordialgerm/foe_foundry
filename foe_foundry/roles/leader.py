from ..ac import ArmorClass
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hit_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=-2, recommended_powers_modifier=1)
    return _as_leader(stats, dials)


def as_low_hp_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, recommended_powers_modifier=1)
    return _as_leader(stats, dials)


def as_low_dmg_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_dice_modifier=-1, recommended_powers_modifier=1)
    return _as_leader(stats, dials)


def _as_leader(stats: BaseStatblock, dials: MonsterDials) -> BaseStatblock:
    new_attributes = (
        stats.attributes.boost(Stats.INT, 4)
        .boost(Stats.WIS, 2)
        .grant_proficiency_or_expertise(Skills.Persuasion)
    )

    if stats.cr >= 4:
        new_attributes = new_attributes.grant_save_proficiency(Stats.INT, Stats.WIS)

    # leaders use shields if possible
    new_ac = stats.ac.delta(
        shield_allowed=ArmorClass.could_use_shield_or_wear_armor(stats.creature_type)
    )

    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Leader, attributes=new_attributes, ac=new_ac
    )


LeaderLowHit = role_variant("Leader.LowHit", MonsterRole.Leader, as_low_hit_leader)
LeaderLowHp = role_variant("Leader.LowHp", MonsterRole.Leader, as_low_hp_leader)
LeaderLowDmg = role_variant("Leader.LowDmg", MonsterRole.Leader, as_low_dmg_leader)
Leader = RoleTemplate("Leader", MonsterRole.Leader, [LeaderLowHit, LeaderLowHp, LeaderLowDmg])
