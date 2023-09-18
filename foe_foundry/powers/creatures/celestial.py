from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_celestial(candidate: BaseStatblock) -> float:
    if candidate.creature_type != CreatureType.Celestial:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _MirroredJudgement(Power):
    """Mirrored Judgment (Reaction). When this creature is the sole target of an attack or spell,
    they can choose another valid target to also be targeted by the attack or spell"""

    def __init__(self):
        super().__init__(name="Mirrored Judgement", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_celestial(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mirrored Judgement",
            action=ActionType.Reaction,
            description="When this creature is the sole target of an attack or spell\
                they can choose another valid target to also be targeted by the attack or spell",
        )

        return stats, feature


class _HealingTouch(Power):
    def __init__(self):
        super().__init__(name="Healing Touch", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_celestial(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        hp = easy_multiple_of_five(int(ceil(max(5, 2 * stats.cr))))

        feature = Feature(
            name="Healing Touch",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=3,
            description=f"{stats.selfref.capitalize()} touches another creature. It magically regains {hp} hp and is freed from any curse, disease, poison, blindness, or deafness",
        )

        return stats, feature


class _RighteousJudgement(Power):
    def __init__(self):
        super().__init__(name="Righteous Judgment", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_celestial(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        dmg = int(ceil(1.5 * stats.attack.average_damage))

        feature = Feature(
            name="Righteous Judgment",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 60 feet. If the target can hear {stats.selfref}, it must make a DC {dc} Charisma save. \
                On a failure, it takes {dmg} radiant damage and is **Blinded** until the end of its next turn. On a success, it takes half as much damage. \
                {stats.selfref.capitalize()} can also choose another friendly creature within 60 feet to gain temporary hp equal to the radiant damage dealt.",
        )

        return stats, feature


HealingTouch: Power = _HealingTouch()
MirroredJudgment: Power = _MirroredJudgement()
RighteousJudgement: Power = _RighteousJudgement()

CelestialPowers: List[Power] = [HealingTouch, MirroredJudgment, RighteousJudgement]
