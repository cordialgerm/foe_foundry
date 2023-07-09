from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hit_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=-2, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_hp_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_dmg_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_dice_modifier=-1, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


LeaderLowHit = role_variant("Leader.LowHit", MonsterRole.Leader, as_low_hit_leader)
LeaderLowHp = role_variant("Leader.LowHp", MonsterRole.Leader, as_low_hp_leader)
LeaderLowDmg = role_variant("Leader.LowDmg", MonsterRole.Leader, as_low_dmg_leader)
Leader = RoleTemplate("Leader", MonsterRole.Leader, [LeaderLowHit, LeaderLowHp, LeaderLowDmg])
