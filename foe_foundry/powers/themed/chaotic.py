from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType, Weakened
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_chaotic(candidate: BaseStatblock, min_cr: float | None = None) -> float:
    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    creature_types = {
        CreatureType.Fey: HIGH_AFFINITY,
        CreatureType.Aberration: HIGH_AFFINITY,
        CreatureType.Humanoid: LOW_AFFINITY,
        CreatureType.Monstrosity: LOW_AFFINITY,
    }
    return creature_types.get(candidate.creature_type, NO_AFFINITY)


class _ChaoticSpace(Power):
    def __init__(self):
        super().__init__(name="Chaotic Space", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_chaotic(candidate, min_cr=5)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        radius = easy_multiple_of_five(stats.cr * 5, min_val=10, max_val=45)
        distance = 30 if stats.cr <= 5 else 60

        feature = Feature(
            name="Chaotic Space",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} creates a region of chaotic space in a {radius} foot sphere centered at a point it can see within {distance} feet. \
                Whenever another creature casts a spell within this space, it must make a DC {dc} Charisma saving throw or trigger a *Wild Magic Surge*. \
                Whenever another creature ends its turn within the space, it teleports 30 (1d10 x 5) feet in a random direction.",
        )

        return stats, feature


class _EldritchBeacon(Power):
    def __init__(self):
        super().__init__(name="Eldritch Beacon", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_chaotic(candidate, min_cr=5)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        hp = easy_multiple_of_five(stats.cr * 5, min_val=5, max_val=30)
        ac = 10
        duration = DieFormula.from_expression("1d4 + 1")

        summon_cr_target = stats.cr / 5

        _, _, description = summoning.determine_summon_formula(
            summoner=stats.creature_type, summon_cr_target=summon_cr_target, rng=rng
        )

        feature = Feature(
            name="Eldritch Beacon",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically creates an Eldritch Beacon (hp {hp}, AC {ac}) at an unoccupied space it can see within 30 feet. \
                {description} After {duration.description} rounds the beacon is destroyed.",
        )

        return stats, feature


ChaoticSpace: Power = _ChaoticSpace()
EldritchBeacon: Power = _EldritchBeacon()

ChaoticPowers: List[Power] = [ChaoticSpace, EldritchBeacon]
