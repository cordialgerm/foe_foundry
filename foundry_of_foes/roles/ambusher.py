import numpy as np

from ..statblocks import BaseStatblock, MonsterDials
from .cycle import VariantCycler

rng = np.random.default_rng(20210518)


def as_low_hp_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2)
    return stats.apply_monster_dials(dials)


def as_low_ac_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9)
    return stats.apply_monster_dials(dials)


AmbusherVariants = {"Ambusher.LowHp": as_low_hp_ambusher, "Ambusher.LowAc": as_low_ac_ambusher}


def as_ambusher(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(AmbusherVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return AmbusherVariants[variant](stats=stats)


__cycler = VariantCycler(keys=list(AmbusherVariants.keys()), method=as_ambusher)


def as_ambusher_cycle(stats: BaseStatblock) -> BaseStatblock:
    return __cycler.execute(stats=stats)
