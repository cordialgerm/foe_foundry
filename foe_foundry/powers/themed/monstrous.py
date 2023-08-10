from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
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


def _score_could_be_monstrous(candidate: BaseStatblock, size_boost: bool = True) -> float:
    score = 0

    creature_types = {
        CreatureType.Monstrosity: HIGH_AFFINITY,
        CreatureType.Beast: HIGH_AFFINITY,
    }
    score += creature_types.get(candidate.creature_type, 0)

    if candidate.size >= Size.Large:
        score += MODERATE_AFFINITY

    return score


def _as_monstrous(
    candidate: BaseStatblock, size_boost: bool = False, boost_speed: int = 10
) -> BaseStatblock:
    changes: dict = dict(attack_type=AttackType.MeleeNatural)
    if size_boost:
        changes.update(size=candidate.size.increment())

    if boost_speed != 0:
        new_speed = candidate.speed.delta(boost_speed)
        changes.update(speed=new_speed)

    return candidate.copy(**changes)


def _score(candidate: BaseStatblock, **args) -> float:
    score = _score_could_be_monstrous(candidate, **args)
    return score if score > 0 else NO_AFFINITY


class _Constriction(Power):
    def __init__(self):
        super().__init__(name="Constriction", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        reach = 5 if stats.size <= Size.Medium else 10
        dc = stats.difficulty_class
        dmg = max(2, ceil(stats.cr))

        feature = Feature(
            name="Constrict",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref} chooses a target it can see within {reach} feet. The target must make a DC {dc} Strength saving throw or become Grappled (escape DC {dc}). \
                While grappled in this way, the target is also Restrained and takes {dmg} ongoing bludgeoning damage at the start of each of its turns.",
        )
        return stats, feature


class _Swallow(Power):
    def __init__(self):
        super().__init__(name="Swallow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, size_boost=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats, size_boost=True)

        reach = 15 if stats.size >= Size.Huge else 10
        new_attack = stats.attack.copy(reach=reach)
        stats = stats.copy(attack=new_attack)

        dc = stats.difficulty_class
        threshold = int(max(5, ceil(2.0 * stats.cr)))
        dmg = int(ceil(5 + stats.cr))
        regurgitate_dc = int(min(25, floor(threshold / 2)))
        feature = Feature(
            name="Swallow",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} attempts to swallow one target within {reach} ft. \
                 The target must make a DC {dc} Dexterity saving throw. On a failure, it is swallowed by {stats.selfref}. \
                A swallowed creature is blinded and restrained, it has total cover against attacks and other effects outside {stats.selfref}, and it takes {dmg} ongoing acid damage at the start of each of its turns.\n\n\
                If {stats.selfref} takes {threshold} damage or more on a single turn from a creature inside it, {stats.selfref} must make a DC {regurgitate_dc} \
                Constitution saving throw at the end of that turn or regurgitate all swallowed creatures, which fall prone in a space within 10 feet of {stats.selfref}. \
                If {stats.selfref} dies, a swallowed creature is no longer restrained by it and can escape from the corpse by using 15 feet of movement, exiting prone.",
        )
        return stats, feature


class _Pounce(Power):
    def __init__(self):
        super().__init__(name="Pounce", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        dc = stats.difficulty_class
        feature = Feature(
            name="Pounce",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} jumps 20 feet toward a creature it can see, attempting to knock it prone. The target must make a DC {dc} Strength save or be knocked prone. \
                Then, {stats.selfref} makes an attack against the target.",
        )

        return stats, feature


Constriction: Power = _Constriction()
Swallow: Power = _Swallow()
Pounce: Power = _Pounce()
MonstrousPowers: List[Power] = [Constriction, Swallow, Pounce]
