from typing import Dict

import numpy as np

from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials

rng = np.random.default_rng(20210518)


def as_low_hit_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=-2, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_hp_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_dmg_leader(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_dice_modifier=-1, recommended_powers_modifier=1)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


LeaderVariants = {
    "Leader.LowHit": as_low_hit_leader,
    "Leader.LowHp": as_low_hp_leader,
    "Leader.LowDmg": as_low_dmg_leader,
}


def as_leader(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(LeaderVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return LeaderVariants[variant](stats=stats)


def as_leader_all(stats: BaseStatblock) -> Dict[str, BaseStatblock]:
    return {k: v(stats=stats) for k, v in LeaderVariants.items()}
