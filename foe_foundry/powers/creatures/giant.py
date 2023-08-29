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
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock) -> float:
    if candidate.creature_type != CreatureType.Giant:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _ForcefulBlow(Power):
    def __init__(self):
        super().__init__(name="Forceful Blow", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        if stats.size >= Size.Gargantuan:
            die = "d8"
        elif stats.size >= Size.Huge:
            die = "d6"
        else:
            die = "d4"

        feature = Feature(
            name="Forceful Blow",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting a target with a weapon attack, {stats.selfref} forcefully pushes the target back. \
                Roll {die}+1. The target is pushed away from {stats.selfref} by 5 times that many feet.",
        )

        return stats, feature


class _ShoveAllies(Power):
    def __init__(self):
        super().__init__(name="Forceful Blow", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shove Allies",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} can shove any allied creatures who are within 5 feet and are smaller in size. \
                Each shoved ally moves up to 15 feet away from {stats.selfref} and can make a melee weapon attack if they end that movement and have a viable target within their reach.",
        )

        return stats, feature


class _Boulder(Power):
    def __init__(self):
        super().__init__(name="Boulder", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy
        if stats.multiattack >= 3:
            dmg = int(floor(1.5 * stats.attack.average_damage))
        else:
            dmg = int(ceil(1.25 * stats.attack.average_damage))

        if stats.cr >= 12:
            distance = 60
            radius = 20
        elif stats.cr >= 8:
            distance = 45
            radius = 15
        elif stats.cr >= 4:
            distance = 30
            radius = 10
        else:
            distance = 20
            radius = 5

        feature = Feature(
            name="Boulder",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} tosses a boulder at a point it can see within {distance} ft. Each creature within a {radius} ft radius must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg} bludgeoning damage and is knocked prone. On a success, the creature takes half damage and is not knocked prone.",
        )

        return stats, feature


ForcefulBlow: Power = _ForcefulBlow()
ShoveAllies: Power = _ShoveAllies()
Boulder: Power = _Boulder()

GiantPowers: List[Power] = [ForcefulBlow, ShoveAllies, Boulder]
