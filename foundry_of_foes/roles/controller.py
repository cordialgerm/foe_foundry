import numpy as n
import numpy as np

from ..statblocks import BaseStatblock, MonsterDials
from .cycle import VariantCycler

rng = np.random.default_rng(20210518)


def as_default_controller(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_modifier=-1, difficulty_class_modifier=2)
    return stats.apply_monster_dials(dials)


ControllerVariants = {"Controller.default": as_default_controller}


def as_controller(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(ControllerVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return ControllerVariants[variant](stats=stats)


__cycler = VariantCycler(keys=list(ControllerVariants.keys()), method=as_controller)


def as_controller_cycle(stats: BaseStatblock) -> BaseStatblock:
    return __cycler.execute(stats=stats)
