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
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _TeleportingStep(Power):
    def __init__(self):
        super().__init__(name="Teleporting Step", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Fey:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        distance = stats.speed.walk
        feature = Feature(
            name="Teleporting Step",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space they can see.",
        )
        return stats, feature


class _BeguilingAura(Power):
    def __init__(self):
        super().__init__(name="Beguiling Aura", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Fey:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Beguiling Aura",
            action=ActionType.Feature,
            description=f"An enemy of {stats.selfref} who moves within 25 of them for the first time on their turn \
                or starts their turn there must succed on a DC {dc} Wisdom saving throw or be charmed by {stats.selfref} until the end of their turn.",
        )
        return stats, feature


TeleportingStep: Power = _TeleportingStep()
BeguilingAura: Power = _BeguilingAura()

FeyPowers: List[Power] = [TeleportingStep, BeguilingAura]
