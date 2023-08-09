from math import ceil, floor
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
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


def _score_could_be_organized(
    candidate: BaseStatblock, requires_intelligence: bool = True
) -> float:
    score = 0

    creature_types = {
        CreatureType.Humanoid: MODERATE_AFFINITY,
        CreatureType.Fey: LOW_AFFINITY,
        CreatureType.Dragon: MODERATE_AFFINITY,
        CreatureType.Giant: LOW_AFFINITY,
    }
    roles = {MonsterRole.Leader: EXTRA_HIGH_AFFINITY}

    if not requires_intelligence:
        creature_types[CreatureType.Beast] = MODERATE_AFFINITY
    elif candidate.attributes.INT <= 8:
        return NO_AFFINITY

    score += creature_types.get(candidate.creature_type, 0)
    score += roles.get(candidate.role, 0)
    return score


def _score(candidate: BaseStatblock) -> float:
    score = _score_could_be_organized(candidate, requires_intelligence=True)
    return score if score > 0 else NO_AFFINITY


class _Commander(Power):
    def __init__(self):
        super().__init__(name="Commander", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 4 else 50
        hp = int(ceil(stats.hp.average / 2))
        bonus = int(ceil(stats.attributes.proficiency / 2))

        feature = Feature(
            name="Commander",
            description=f"When {stats.selfref} is at or above {hp} hp then each other ally within {distance} has a + {bonus} bonus to attack and damage rolls",
            action=ActionType.Feature,
        )

        return stats, feature


class _Fanatic(Power):
    def __init__(self):
        super().__init__(name="Fanatic", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 4 else 50
        hp = int(ceil(stats.hp.average / 2))
        temp = int(max(floor(5 + stats.cr), 1.5 * stats.cr))

        feature = Feature(
            name="Fanaticism",
            description=f"When {stats.selfref} is at or below {hp} hp then each other ally within {distance} ft has advantage on attack rolls.\
                When an ally hits with an attack, then {stats.selfref} gains {temp} temp hp.",
            action=ActionType.Feature,
        )

        return stats, feature


class _Inspiring(Power):
    def __init__(self):
        super().__init__(name="Inspiring", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        hp = int(floor(5 + stats.cr / 2))

        feature = Feature(
            name="Inspiring",
            description=f"When {stats.selfref} succeeds on a saving throw or when an attack roll misses them, one ally who {stats.selfref} can see gains {hp} temp hp.",
            action=ActionType.Reaction,
        )

        return stats, feature


Commander: Power = _Commander()
Fanatic: Power = _Fanatic()
Inspiring: Power = _Inspiring()

OrganizedPowers: List[Power] = [Commander, Fanatic, Inspiring]
