from math import ceil, floor
from typing import List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_flyer(candidate: BaseStatblock, require_flying: bool = False) -> float:
    if require_flying and not candidate.speed.fly:
        return NO_AFFINITY

    creature_types = {
        CreatureType.Dragon: EXTRA_HIGH_AFFINITY,
        CreatureType.Fiend: EXTRA_HIGH_AFFINITY,
        CreatureType.Celestial: EXTRA_HIGH_AFFINITY,
        CreatureType.Aberration: HIGH_AFFINITY,
        CreatureType.Beast: MODERATE_AFFINITY,
        CreatureType.Monstrosity: MODERATE_AFFINITY,
        CreatureType.Elemental: MODERATE_AFFINITY,
        CreatureType.Fey: MODERATE_AFFINITY,
    }

    return creature_types.get(candidate.creature_type, NO_AFFINITY)


class _Flyer(PowerBackport):
    def __init__(self):
        super().__init__(name="Flyer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_flyer(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        speed_change = 10 + 10 * int(floor(stats.cr / 10.0))
        new_speed = stats.speed.delta(speed_change=speed_change)
        new_speed = new_speed.copy(fly=new_speed.walk)
        stats = stats.copy(speed=new_speed)

        feature = Feature(
            name="Flyer",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement speed increases by {speed_change} and it gains a fly speed equal to its walk speed",
            hidden=True,
        )

        return stats, feature


class _Flyby(PowerBackport):
    def __init__(self):
        super().__init__(name="Flyby", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_flyer(candidate, require_flying=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        feature = Feature(
            name="Flyby",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} does not provoke opportunity attacks.",
        )

        return stats, feature


Flyer: Power = _Flyer()
Flyby: Power = _Flyby()

FlyerPowers: List[Power] = [Flyer, Flyby]
