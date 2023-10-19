from math import ceil, floor
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
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_could_be_organized(
    candidate: BaseStatblock, requires_intelligence: bool = True
) -> float:
    creature_types = {c for c in CreatureType if c.could_be_organized}
    if not requires_intelligence:
        creature_types |= {CreatureType.Beast}

    return score(
        candidate=candidate,
        require_types=creature_types,
        bonus_roles=MonsterRole.Leader,
        require_stats=Stats.INT if requires_intelligence else None,
    )


class _Commander(PowerBackport):
    def __init__(self):
        super().__init__(name="Commander", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_could_be_organized(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 4 else 50
        hp = easy_multiple_of_five(int(ceil(stats.hp.average / 2)))
        bonus = int(ceil(stats.attributes.proficiency / 2))

        feature = Feature(
            name="Commander",
            description=f"When {stats.roleref} is at or above {hp} hp then each other ally within {distance} ft. has a +{bonus} bonus to attack and damage rolls",
            action=ActionType.Feature,
        )

        return stats, feature


class _Fanatic(PowerBackport):
    def __init__(self):
        super().__init__(name="Fanatic", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_could_be_organized(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 4 else 50
        hp = easy_multiple_of_five(int(ceil(stats.hp.average / 2)))
        temp = easy_multiple_of_five(int(max(floor(5 + stats.cr), 1.5 * stats.cr)))

        feature = Feature(
            name="Fanaticism",
            description=f"When {stats.roleref} is at or below {hp} hp then each other ally within {distance} ft has advantage on attack rolls.\
                When an ally hits with an attack, then {stats.roleref} gains {temp} temp hp.",
            action=ActionType.Feature,
        )

        return stats, feature


class _Inspiring(PowerBackport):
    def __init__(self):
        super().__init__(name="Inspiring", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_could_be_organized(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        hp = easy_multiple_of_five(int(floor(5 + stats.cr / 2)))

        feature = Feature(
            name="Inspiring",
            description=f"When {stats.roleref} succeeds on a saving throw or when an attack roll misses them, one ally who {stats.roleref} can see gains {hp} temp hp.",
            action=ActionType.Reaction,
        )

        return stats, feature


Commander: Power = _Commander()
Fanatic: Power = _Fanatic()
Inspiring: Power = _Inspiring()

OrganizedPowers: List[Power] = [Commander, Fanatic, Inspiring]
