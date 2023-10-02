from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
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


def score_artillery(candidate: BaseStatblock, speed_bonus: bool = False) -> float:
    if not candidate.attack_type.is_ranged():
        return NO_AFFINITY

    score = MODERATE_AFFINITY

    if candidate.role == MonsterRole.Artillery:
        score += MODERATE_AFFINITY

    if candidate.attributes.INT >= 15:
        score += LOW_AFFINITY

    if candidate.attributes.has_proficiency_or_expertise(Skills.Perception):
        score += LOW_AFFINITY

    if speed_bonus and (
        candidate.role == MonsterRole.Skirmisher or candidate.speed.fastest_speed >= 40
    ):
        score += LOW_AFFINITY

    return score


class _Ricochet(Power):
    def __init__(self):
        super().__init__(name="Richochet", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Ricochet",
            action=ActionType.Reaction,
            description=f"When {stats.roleref} misses with a ranged attack, it can make the same attack again against a different target within 15 ft of the original target.",
        )

        return stats, feature


class _SteadyAim(Power):
    def __init__(self):
        super().__init__(name="Steady Aim", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
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
        return score_artillery(candidate, speed_bonus=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Quick Step",
            action=ActionType.BonusAction,
            description=f"Before {stats.roleref} makes a ranged attack, they can first move 5 feet without provoking opportunity attacks",
        )
        return stats, feature


class _QuickDraw(Power):
    def __init__(self):
        super().__init__(name="Quick Draw", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        uses = ceil(stats.cr / 5)
        feature = Feature(
            name="Quick Draw",
            action=ActionType.Reaction,
            description=f"On initiative count 20, {stats.selfref} may make one ranged attack",
            uses=uses,
        )

        return stats, feature


class _SuppressingFire(Power):
    def __init__(self):
        super().__init__(name="Suppressing Fire", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Suppressing Fire",
            action=ActionType.Feature,
            description=f"On a hit, the target's speed is reduced by half until the end of its next turn",
            hidden=True,
            modifies_attack=True,
        )

        return stats, feature


class _IndirectFire(Power):
    def __init__(self):
        super().__init__(name="Indirect Fire", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Indirect Fire",
            action=ActionType.Feature,
            description=f"{stats.roleref} can perform its ranged attacks indirectly, such as by arcing or curving shots. It ignores half and three-quarters cover. \
                These attacks are often unexpected. If it makes a ranged attack against a creature with half or three-quarters cover that is not yet aware of this ability, the attack is made at advantage. \
                Any creature that can see the attack occuring is then aware of this ability.",
        )

        return stats, feature


class _Overwatch(Power):
    def __init__(self):
        super().__init__(name="Overwatch", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_artillery(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Overwatch",
            action=ActionType.Reaction,
            recharge=4,
            description=f"When a hostile creature within 60 feet of {stats.roleref} moves and {stats.roleref} can see that movement, it can make a ranged attack against the target.",
        )

        return stats, feature


IndirectFire: Power = _IndirectFire()
Overwatch: Power = _Overwatch()
Richochet: Power = _Ricochet()
SteadyAim: Power = _SteadyAim()
QuickStep: Power = _QuickStep()
QuickDraw: Power = _QuickDraw()
SuppresingFire: Power = _SuppressingFire()


ArtilleryPowers: List[Power] = [
    IndirectFire,
    Overwatch,
    QuickStep,
    QuickDraw,
    Richochet,
    SteadyAim,
    SuppresingFire,
]
