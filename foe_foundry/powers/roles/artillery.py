from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Ricochet(Power):
    def __init__(self):
        super().__init__(name="Richochet", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Artillery:
            score += MODERATE_AFFINITY

        if candidate.attributes.INT >= 15:
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Ricochet",
            action=ActionType.Reaction,
            description=f"When {stats.roleref} misses with a ranged attack, it can make the same attack again against a different target within 15 ft.",
        )

        return stats, feature


class _SteadyAim(Power):
    def __init__(self):
        super().__init__(name="Steady Aim", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Artillery:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Perception):
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Steady Aim",
            action=ActionType.BonusAction,
            description=f"If {stats.roleref} has not moved this turn, it gains advantage on the next ranged attack roll it makes this turn and ignores partial or half cover for that attack.\
                Its speed becomes 0 until the start of its next turn.",
        )

        return stats, feature


class _QuickStep(Power):
    def __init__(self):
        super().__init__(name="Quick Step", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Artillery:
            score += MODERATE_AFFINITY

        if candidate.speed.fastest_speed >= 40:
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Quick Step",
            action=ActionType.Reaction,
            description=f"When {stats.roleref} would make a ranged attack, they can first move 5 feet without provoking opportunity attacks",
        )
        return stats, feature


class _QuickDraw(Power):
    def __init__(self):
        super().__init__(name="Quick Draw", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Artillery:
            score += MODERATE_AFFINITY

        if candidate.attributes.INT >= 15:
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Quick Draw",
            action=ActionType.Reaction,
            description=f"On initiative count 20, {stats.selfref} may make one ranged attack",
            uses=1,
        )

        return stats, feature


class _SuppressingFire(Power):
    def __init__(self):
        super().__init__(name="Suppressing Fire", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Artillery:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Perception):
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Suppressing Fire",
            action=ActionType.Feature,
            description=f"When {stats.roleref} hits a target with a ranged attack, that target's speed is reduced by half until the end of its next turn",
        )

        return stats, feature


Richochet: Power = _Ricochet()
SteadyAim: Power = _SteadyAim()
QuickStep: Power = _QuickStep()
QuickDraw: Power = _QuickDraw()
SuppresingFire: Power = _SuppressingFire()


ArtilleryPowers: List[Power] = [Richochet, SteadyAim, QuickStep, QuickDraw, SuppresingFire]
