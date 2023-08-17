from math import ceil, floor
from typing import List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _EmpoweredByDeath(Power):
    def __init__(self):
        super().__init__(name="Empowered by Death", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Fiend:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        hp = int(floor(5 + 2 * stats.cr))

        feature = Feature(
            name="Empowered by Death",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp whenever a creature dies within 30 ft. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        return stats, feature


class _RelishYourFailure(Power):
    def __init__(self):
        super().__init__(name="Relish Your Failure", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Fiend:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        hp = int(ceil(stats.cr / 2))

        feature = Feature(
            name="Relish Your Failure",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp whenever a creature fails a saving throw within 60 feet. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        return stats, feature


EmpoweredByDeath: Power = _EmpoweredByDeath()
RelishYourFailure: Power = _RelishYourFailure()

FiendishPowers: List[Power] = [EmpoweredByDeath, RelishYourFailure]
