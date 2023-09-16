from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_psychic(candidate: BaseStatblock) -> float:
    # this is great for aberrations, psychic focused creatures, and controllers
    score = 0

    if candidate.creature_type == CreatureType.Aberration:
        score += HIGH_AFFINITY
    if candidate.secondary_damage_type == DamageType.Psychic:
        score += HIGH_AFFINITY
    if candidate.role == MonsterRole.Controller:
        score += MODERATE_AFFINITY
    return score if score > 0 else NO_AFFINITY


class _Telekinetic(Power):
    """This creature chooses one creature they can see within 100 feet of them
    weighing less than 400 pounds. The target must succeed on a Strength saving throw
    (DC = 11 + 1/2 CR) or be pulled up to 80 feet directly toward this creature."""

    def __init__(self):
        super().__init__(name="Telekinetic", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        dc = int(ceil(11 + stats.cr / 2.0))

        feature = Feature(
            name="Telekinetic Grasp",
            description=f"{stats.selfref.capitalize()} chooses one creature they can see within 100 feet weighting less than 400 pounds. \
                The target must succeed on a DC {dc} Strength saving throw or be pulled up to 80 feet directly toward {stats.selfref}",
            action=ActionType.BonusAction,
        )
        return stats, feature


Telekinetic: Power = _Telekinetic()

PsychicPowers: List[Power] = [Telekinetic]
