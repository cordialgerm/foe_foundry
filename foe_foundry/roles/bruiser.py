from typing import Dict

import numpy as np

from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials

rng = np.random.default_rng(20210518)


def as_low_hit_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=-2, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


def as_low_hp_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9, attack_hit_modifier=-1, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


def as_low_ac_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


BruteVariants = {
    "Brute.LowHit": as_low_hit_bruiser,
    "Brute.LowHp": as_low_hp_bruiser,
    "Brute.LowAc": as_low_ac_bruiser,
}


def as_bruiser(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(BruteVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return BruteVariants[variant](stats=stats)


def as_bruiser_all(stats: BaseStatblock) -> Dict[str, BaseStatblock]:
    return {k: v(stats=stats) for k, v in BruteVariants.items()}
