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
from ...damage import AttackType, DamageType
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


def _score(candidate: BaseStatblock, undead_only: bool = False) -> float:
    score = 0

    if candidate.creature_type == CreatureType.Undead:
        score += HIGH_AFFINITY

    if not undead_only and candidate.creature_type == CreatureType.Fiend:
        score += MODERATE_AFFINITY

    if candidate.secondary_damage_type == DamageType.Necrotic:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _AuraOfDoom(Power):
    def __init__(self):
        super().__init__(name="Aura of Doom", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 7 else 50

        feature = Feature(
            name="Aura of Doom",
            description=f"Each enemy within {distance} ft of {stats.selfref} who makes a death saving throw does so at disadvantage.",
            action=ActionType.Feature,
        )

        return stats, feature


class _AuraOfAnnihilation(Power):
    def __init__(self):
        super().__init__(name="Aura of Annihilation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 5 if stats.cr <= 11 else 10
        dmg = max(5 + stats.cr, 1.5 * stats.cr)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Aura of Annihilation",
            description=f"Each creature who ends their turn within {distance} ft of {stats.selfref} must make a DC {dc} Constitution saving throw. \
                On a failure, they take {dmg} necrotic damage and gain one Death Save failure. With three failures, a creature dies. \
                On a success, a creature takes half damage and does not gain a Death Save failure. With three successes, a creature is immune to this effect",
            action=ActionType.Feature,
        )

        return stats, feature


class _UndyingMinions(Power):
    def __init__(self):
        super().__init__(name="Undying Minions", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Undying Minions",
            description=f"When a non-zombie ally who can see {stats.selfref} is reduced to 0 hp, that ally immediately becomes a zombie (retaining its current stats). \
                The ally gains the Undead type and stands up with 1 hit point. If damage reduces the zombie to 0 hit points, it may make a DC 15 Constitution saving throw. \
                On a success, the zombie drops to 1 hit point instead.",
            action=ActionType.Feature,
        )

        return stats, feature


class _WitheringBlow(Power):
    def __init__(self):
        super().__init__(name="Withering Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        dmg = int(floor(3 + stats.cr))

        feature = Feature(
            name="Withering Blow",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting with an attack, the target takes an additional {dmg} ongoing necrotic damage at the start of each of their turns. \
                The effect can be ended by any character using an action to perform a DC {dc} Medicine check or if the target receives {dmg} or more points of magical healing in a round.",
        )

        return stats, feature


class _DrainingBlow(Power):
    def __init__(self):
        super().__init__(name="Draining Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        feature = Feature(
            name="Draining Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack that deals necrotic damage, the {stats.selfref} regains hit points equal to the necrotic damage dealt.",
        )

        return stats, feature


AuraOfDoom: Power = _AuraOfDoom()
AuraOfAnnihilation: Power = _AuraOfAnnihilation()
UndyingMinions: Power = _UndyingMinions()
WitheringBlow: Power = _WitheringBlow()
DrainingBlow: Power = _DrainingBlow()

DeathlyPowers: List[Power] = [
    AuraOfDoom,
    AuraOfAnnihilation,
    UndyingMinions,
    WitheringBlow,
    DrainingBlow,
]
