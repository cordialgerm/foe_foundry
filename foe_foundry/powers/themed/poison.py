from math import ceil, floor
from typing import List, Tuple

import numpy as np

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
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


def _score(candidate: BaseStatblock) -> float:
    creature_types = {
        CreatureType.Plant: HIGH_AFFINITY,
        CreatureType.Aberration: LOW_AFFINITY,
        CreatureType.Monstrosity: LOW_AFFINITY,
    }
    score = creature_types.get(candidate.creature_type, 0)

    if candidate.secondary_damage_type == DamageType.Poison:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _PoisonousDemise(Power):
    def __init__(self):
        super().__init__(name="Poisonous Demise", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(secondary_damage_type=DamageType.Poison)

        dmg = DieFormula.target_value(2 + stats.cr, force_die=Die.d4)
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 4, min_val=10, max_val=60)

        feature = Feature(
            name="Poisonous Demise",
            description=f"When {stats.selfref} dies, they release a spray of poison. Each creature within {distance} ft must succeed on a DC {dc} Dexterity save or take {dmg.description} poison damage",
            action=ActionType.Reaction,
        )

        return stats, feature


class _VirulentPoison(Power):
    def __init__(self):
        super().__init__(name="Virulent Poison", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        stats = stats.copy(secondary_damage_type=DamageType.Poison)

        feature1 = Feature(
            name="Virulent Poison",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s attacks that deal poison damage ignore a target's resistance to poison damage. \
                If a target has immunity to poison damage, it instead has resistance to poison damage against this creature's attacks.",
        )

        feature2 = Feature(
            name="Virulent Poison",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description="On a hit, the target is **Poisoned** until the end of their next turn.",
        )

        return stats, [feature1, feature2]


PoisonousDemise: Power = _PoisonousDemise()
VirulentPoison: Power = _VirulentPoison()

PoisonPowers: List[Power] = [PoisonousDemise, VirulentPoison]
