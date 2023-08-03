from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _PinningShot(Power):
    def __init__(self):
        super().__init__(name="Pinning Shot", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.attack_type.is_ranged():
            score += MODERATE_AFFINITY

        if candidate.role == MonsterRole.Controller:
            score += MODERATE_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # TODO - modify attack action directly

        dc = stats.difficulty_class

        feature = Feature(
            name="Pinning Shot",
            action=ActionType.Feature,
            description=f"When the {stats.selfref} hits with a ranged attack, the target must succeed on a DC {dc} Strength saving throw or be Restrained (save ends at end of turn).",
        )

        return stats, feature


PinningShot: Power = _PinningShot()
