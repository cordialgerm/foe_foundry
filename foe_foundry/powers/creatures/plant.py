from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock) -> float:
    if candidate.creature_type != CreatureType.Plant:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _PoisonThorns(Power):
    def __init__(self):
        super().__init__(name="Poison Thorns", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = int(ceil(stats.attack.average_damage / 2))
        feature = Feature(
            name="Poison Thorns",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after {stats.selfref} hits a target with an attack, the attack deals an additional {dmg} poison damage and the target is **Poisoned** until the end of their next turn.",
        )
        return stats, feature


class _GraspingRoots(Power):
    def __init__(self):
        super().__init__(name="Grasping Roots", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Grasping Roots",
            action=ActionType.Reaction,
            description=f"When a creature attempts to leave a space within 5 feet of {stats.selfref} then it must make a DC {dc} Strength save. \
                On a failure, the creature is restrained until the start of its next turn and {stats.selfref} may also make an opportunity attack against the creature.",
        )
        return stats, feature


PoisonThorns: Power = _PoisonThorns()
GraspingRoots: Power = _GraspingRoots()

PlantPowers: List[Power] = [PoisonThorns, GraspingRoots]
