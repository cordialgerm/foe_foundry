from math import floor
from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_sneaky_creature(
    candidate: BaseStatblock, additional_creature_types: Set[CreatureType] | None = None
) -> float:
    score = 0

    if candidate.role == MonsterRole.Ambusher:
        score += HIGH_AFFINITY

    if candidate.role == MonsterRole.Skirmisher:
        score += MODERATE_AFFINITY

    if candidate.primary_attribute == Stats.DEX:
        score += LOW_AFFINITY

    if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
        score += MODERATE_AFFINITY

    if (
        additional_creature_types is not None
        and candidate.creature_type in additional_creature_types
    ):
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _CunningAction(Power):
    def __init__(self):
        super().__init__(name="Cunning Action", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Cunning Action",
            description="Dash, Disengage, or Hide",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _SneakyStrike(Power):
    def __init__(self):
        super().__init__(name="Sneaky Strike", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dmg = int(floor(max(2 * stats.cr, 2 + stats.cr)))

        feature = Feature(
            name="Sneaky Strike",
            description=f"{stats.roleref.capitalize()} deals an additional {dmg} damage immediately after hitting a target if the attack was made with advantage.",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _FalseAppearance(Power):
    def __init__(self):
        super().__init__(name="False Appearance", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(
            candidate, additional_creature_types={CreatureType.Plant, CreatureType.Construct}
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="False Appearance",
            action=ActionType.Feature,
            description=f"As long as {stats.selfref} remains motionless it is indistinguishable from its surrounding terrain.",
        )

        return stats, feature


CunningAction: Power = _CunningAction()
FalseAppearance: Power = _FalseAppearance()
SneakyStrike: Power = _SneakyStrike()


SneakyPowers: List[Power] = [CunningAction, FalseAppearance, SneakyStrike]
