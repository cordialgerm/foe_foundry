from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DragonsGaze(Power):
    def __init__(self):
        super().__init__(name="Dragon's Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Dragon:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        dc = stats.difficulty_class
        dmg = int(max(3, stats.cr / 2))

        feature = Feature(
            name="Dragon's Gaze",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"One creature within 60 feet of {stats.selfref} must make a DC {dc} Wisdom save or be frightened of {stats.selfref}. \
                While frightened in this way, each time the target takes damage, they take an additional {dmg} damage. Save ends at end of turn.",
        )

        return stats, feature


DragonsGaze: Power = _DragonsGaze()


DragonPowers: List[Power] = [DragonsGaze]
