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
from ..scoring import score


def score_flyer(candidate: BaseStatblock, require_flying: bool = False) -> float:
    def is_flyer(c: BaseStatblock) -> bool:
        return (candidate.speed.fly or 0) > 0

    creature_types = {
        CreatureType.Dragon,
        CreatureType.Fiend,
        CreatureType.Celestial,
        CreatureType.Aberration,
        CreatureType.Beast,
        CreatureType.Monstrosity,
        CreatureType.Elemental,
        CreatureType.Fey,
    }

    return score(
        candidate=candidate,
        require_types=creature_types,
        require_callback=is_flyer if require_flying else None,
    )


class _Flyer(PowerBackport):
    def __init__(self):
        super().__init__(name="Flyer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_flyer(candidate)

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
        return score_flyer(candidate, require_flying=True)

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
