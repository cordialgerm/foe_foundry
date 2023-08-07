from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
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


class _ElementalShroud(Power):
    def __init__(self):
        super().__init__(name="Elemental Shroud", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.secondary_damage_type is not None:
            score += LOW_AFFINITY

        if candidate.creature_type == CreatureType.Elemental:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dmg_type = stats.secondary_damage_type or DamageType.Fire
        dmg = int(ceil(5 + stats.cr))

        feature = Feature(
            name="Elemental Shroud",
            description=f"When {stats.selfref} is hit by a melee attack, their body is shrouded with {dmg_type} energy.\
                Until the start of their next turn, any creature who touches {stats.selfref} or hits them with a melee attack takes {dmg} {dmg_type} damage.",
            uses=1,
            action=ActionType.Reaction,
        )

        return stats, feature


ElementalShroud: Power = _ElementalShroud()

ElementalPowers: List[Power] = [ElementalShroud]
