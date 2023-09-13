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
    if candidate.creature_type != CreatureType.Undead:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _UndeadResilience(Power):
    def __init__(self):
        super().__init__(name="Undead Resilience", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Undaed Resilience",
            action=ActionType.Reaction,
            description=f"When damage reduces {stats.selfref} to 0 hit points, it must make a Constitution saving throw with a DC of 2 + the damage taken, \
                unless the damage is radiant or from a critical hit. On a success, {stats.selfref} instead drops to 1 hit point.",
        )
        return stats, feature


class _StenchOfDeath(Power):
    def __init__(self):
        super().__init__(name="Stench of Death", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Stench of Death",
            action=ActionType.Feature,
            description=f"Any creature that starts its turn within 10 feet of {stats.selfref} must make a DC {dc} Constitution saving throw or become poisoned until the start of their next turn. \
                On a successful saving throw, the creature is immune to {stats.selfref}'s stench for 24 hours.",
        )
        return stats, feature


UndeadResilience: Power = _UndeadResilience()
StenchOfDeath: Power = _StenchOfDeath()

UndeadPowers: List[Power] = [UndeadResilience, StenchOfDeath]
