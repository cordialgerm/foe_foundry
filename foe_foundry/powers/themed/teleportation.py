from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
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


def _score_has_teleport(candidate: BaseStatblock) -> float:
    score = 0

    creature_types = {
        CreatureType.Fey: HIGH_AFFINITY,
        CreatureType.Fiend: MODERATE_AFFINITY,
        CreatureType.Aberration: HIGH_AFFINITY,
        CreatureType.Humanoid: MODERATE_AFFINITY,
    }
    score += creature_types.get(candidate.creature_type, 0)

    if score == 0:
        return 0

    roles = {MonsterRole.Ambusher: LOW_AFFINITY, MonsterRole.Controller: HIGH_AFFINITY}
    score += roles.get(candidate.role, 0)

    if candidate.attack_type.is_spell():
        score += LOW_AFFINITY

    return score


class _BendSpace(Power):
    def __init__(self):
        super().__init__(name="Bend Space", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_has_teleport(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Bend Space",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} would be hit by an attack, it teleports and exchanges position with an ally it can see within 60 feet of it. The ally is then hit by the attack instead.",
        )

        return stats, feature


class _MistyStep(Power):
    def __init__(self):
        super().__init__(name="Misty Step", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_has_teleport(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 7 else 60
        uses = int(min(3, ceil(stats.cr / 3)))

        feature = Feature(
            name="Misty Step",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space it can see.",
        )

        return stats, feature


class _Scatter(Power):
    def __init__(self):
        super().__init__(name="Scatter", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_has_teleport(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        distance = 20 if stats.cr <= 7 else 30
        dc = stats.difficulty_class
        count = int(max(2, ceil(stats.cr / 3)))

        feature = Feature(
            name="Scatter",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} forces up to {count} creatures it can see within {distance} feet to make a DC {dc} Charisma save. \
                On a failure, the target is teleported to an unoccupied space within {4 * distance} feet that {stats.selfref} can see. The space must be on the ground or on a floor.",
        )

        return stats, feature


BendSpace: Power = _BendSpace()
MistyStep: Power = _MistyStep()
Scatter: Power = _Scatter()

TeleportationPowers: List[Power] = [BendSpace, MistyStep, Scatter]
