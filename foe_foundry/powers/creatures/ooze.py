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
    if candidate.creature_type != CreatureType.Ooze:
        return NO_AFFINITY

    return HIGH_AFFINITY


def malleable_form(stats: BaseStatblock) -> Feature:
    size = stats.size.decrement().decrement()
    return Feature(
        name="Malleable Form",
        action=ActionType.Feature,
        description=f"{stats.selfref.capitalize()} has advantage on checks to begin or escape a grapple, \
                and can move through a space as if {stats.selfref} were {size} without squeezing.",
    )


class _OozingPassage(Power):
    def __init__(self):
        super().__init__(name="Oozing Passage", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        size = stats.size
        dc = stats.difficulty_class
        feature = Feature(
            name="Oozing Passage",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can move through the space of other creatures of size {size} or smaller \
                without provoking opportunity attacks. When {stats.selfref} does so, each creature {stats.selfref} moves through must succed on a \
                DC {dc} Strength save or be restrained until the end of their next turn.",
        )
        return stats, [malleable_form(stats), feature]


class _ElongatedLimbs(Power):
    def __init__(self):
        super().__init__(name="Elongated Limbs", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        feature = Feature(
            name="Elongated Limbs",
            action=ActionType.Reaction,
            description=f"{stats.selfref.capitalize()} may make an opportunity attack whenever a creature moves in or out of {stats.selfref}'s reach.",
        )
        new_attack = stats.attack.copy(reach=stats.attack.reach or 0 + 5)
        stats = stats.copy(attack=new_attack)
        return stats, [malleable_form(stats), feature]


OozingPassage: Power = _OozingPassage()
ElongatedLimbs: Power = _ElongatedLimbs()

OozePowers: List[Power] = [OozingPassage, ElongatedLimbs]
