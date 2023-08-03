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


class _MirroredJudgement(Power):
    """Mirrored Judgment (Reaction). When this creature is the sole target of an attack or spell,
    they can choose another valid target to also be targeted by the attack or spell"""

    def __init__(self):
        super().__init__(name="Mirrored Judgement", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Celestial:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mirrored Judgement",
            action=ActionType.Reaction,
            description="When this creature is the sole target of an attack or spell\
                they can choose another valid target to also be targeted by the attack or spell",
        )

        return stats, feature


MirroredJudgment: Power = _MirroredJudgement()

CelestialPowers: List[Power] = [MirroredJudgment]
