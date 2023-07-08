from typing import Dict

import numpy as np

from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials

rng = np.random.default_rng(20210518)


def as_low_ac_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, speed_modifier=20)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_hp_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, speed_modifier=20)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


SkirmisherVariants = {
    "Skirmisher.LowAc": as_low_ac_skirmisher,
    "Skirmisher.LowHp": as_low_hp_skirmisher,
}


def as_skirmisher(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(SkirmisherVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return SkirmisherVariants[variant](stats=stats)


def as_skirmisher_all(stats: BaseStatblock) -> Dict[str, BaseStatblock]:
    return {k: v(stats=stats) for k, v in SkirmisherVariants.items()}
