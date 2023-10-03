from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_temporal(candidate: BaseStatblock, min_cr: float | None = None) -> float:
    score = 0

    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    if candidate.creature_type in {
        CreatureType.Fey,
        CreatureType.Fiend,
        CreatureType.Aberration,
    }:
        score += HIGH_AFFINITY

    if candidate.attack_type.is_spell():
        score += MODERATE_AFFINITY

    if candidate.role in {MonsterRole.Controller}:
        score += MODERATE_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _CurseOfTheAges(Power):
    def __init__(self):
        super().__init__(name="Curse of the Ages", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=7)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(2.5 * stats.attack.average_damage, force_die=Die.d12)

        feature = Feature(
            name="Curse of the Ages",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 90 feet and curses it with rapid aging. \
                The target must make a DC {dc} Constitution saving throw, taking {dmg.description} necrotic damage on a failed save, or half as much on a success. \
                On a failure, the target also ages to the point where it has only 30 days left before it dies of old age. \
                Only a *wish* spell or *greater restoration* cast with a 9th-level spell slot can end this effect and restore the target to its previous age.",
        )

        return stats, feature


class _TemporalLoop(Power):
    def __init__(self):
        super().__init__(name="Temporal Loop", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=3)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        distance = 30
        uses = ceil(stats.cr / 7)

        feature1 = Feature(
            name="Temporal Record",
            action=ActionType.Feature,
            description=f"Whenever another creature within {distance} feet makes a d20 test, {stats.selfref} can record the d20 result (no action required). \
                If it already has a result recorded, then that result is overwritten with the new die roll.",
        )

        feature2 = Feature(
            name="Temporal Loop",
            action=ActionType.Reaction,
            uses=uses,
            description=f"Whenever a creature within {distance} feet makes a d20 test, {stats.selfref} can replace the result of the d20 roll \
                            with the die result it has recorded with its *Temporal Record* feature. The die result is then cleared.",
        )

        return stats, [feature1, feature2]


class _TemporalMastery(Power):
    def __init__(self):
        super().__init__(name="Temporal Mastery", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=7)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Temporal Mastery",
            action=ActionType.Action,
            uses=2,
            replaces_multiattack=1,
            description=f"{stats.selfref} becomes **Invisible** until the start of its next turn. It may also adjust its initiative to any value it desires. \
                This can allow {stats.selfref} to have a second turn this round.",
        )

        return stats, feature


CurseOfTheAges: Power = _CurseOfTheAges()
TemporalLoop: Power = _TemporalLoop()
TemporalMastery: Power = _TemporalMastery()

TemporalPowers: List[Power] = [CurseOfTheAges, TemporalLoop, TemporalMastery]
