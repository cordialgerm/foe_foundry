from math import ceil, floor
from typing import List, Set, Tuple

import numpy as np
from num2words import num2words
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Shocked
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_storm(candidate: BaseStatblock, min_cr: float | None = None) -> float:
    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    if (
        candidate.secondary_damage_type is not None
        and candidate.secondary_damage_type != DamageType.Lightning
    ):
        return NO_AFFINITY

    creature_types = {
        CreatureType.Elemental: HIGH_AFFINITY,
        CreatureType.Giant: HIGH_AFFINITY,
        CreatureType.Dragon: MODERATE_AFFINITY,
        CreatureType.Humanoid: MODERATE_AFFINITY,
    }

    score = creature_types.get(candidate.creature_type, 0)

    if candidate.secondary_damage_type in {DamageType.Lightning, DamageType.Thunder}:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


def as_stormy(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type != DamageType.Lightning:
        stats = stats.copy(secondary_damage_type=DamageType.Lightning)

    return stats


class _TempestSurge(Power):
    def __init__(self):
        super().__init__(name="Tempest Surge", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_storm(candidate, min_cr=3)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_stormy(stats)

        dmg = DieFormula.target_value(
            target=2.5 * stats.attack.average_damage, force_die=Die.d10
        )
        shocked = Shocked()
        dc = stats.difficulty_class

        feature = Feature(
            name="Tempest Surge",
            action=ActionType.Action,
            replaces_multiattack=3,
            recharge=5,
            description=f"{stats.selfref.capitalize()} sends out arcs of lightning at a creature it can see within 60 feet. \
                The creature must make a DC {dc} Dexterity saving throw. On a failure, the target takes {dmg.description} lightning damage \
                and is {shocked}. On a success, the creature takes half damage instead.",
        )

        return stats, feature


class _StormcallersFury(Power):
    def __init__(self):
        super().__init__(name="Stormcaller's Fury", power_type=PowerType.Theme)
        self.min_cr = 3

    def score(self, candidate: BaseStatblock) -> float:
        return score_storm(candidate, min_cr=self.min_cr)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_stormy(stats)

        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(
            target=1.5 * stats.attack.average_damage, force_die=Die.d10
        )

        feature = Feature(
            name="Stormcaller's Fury",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} calls down lightning on a point it can see within 120 feet. \
                Each creature within 5 feet of the point must make a DC {dc} Dexterity saving throw, taking {dmg.description} \
                lightning damage on a failure and half damage on a success. If the outdoors are in stormy conditions then this save is made with disadvantage.",
        )

        return stats, feature


TempestSurge: Power = _TempestSurge()
StormcallersFury: Power = _StormcallersFury()

StormPowers: List[Power] = [StormcallersFury, TempestSurge]