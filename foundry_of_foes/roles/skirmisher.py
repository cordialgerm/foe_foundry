import numpy as n
import numpy as np

from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials
from .cycle import VariantCycler

rng = np.random.default_rng(20210518)


def as_low_ac_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, speed_modifier=20)
    return stats.apply_monster_dials(dials)


def as_low_hp_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, speed_modifier=20)
    return stats.apply_monster_dials(dials)


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


__cycler = VariantCycler(keys=list(SkirmisherVariants.keys()), method=as_skirmisher)


def as_skirmisher_cycle(stats: BaseStatblock) -> BaseStatblock:
    return __cycler.execute(stats=stats)
