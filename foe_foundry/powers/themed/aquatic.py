from math import ceil, floor
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

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


class _Aquatic(Power):
    def __init__(self):
        super().__init__(name="Aquatic", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0
        if candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        if candidate.secondary_damage_type == DamageType.Cold:
            score += HIGH_AFFINITY
        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(swim=stats.speed.walk)
        new_senses = stats.senses.copy(darkvision=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)

        feature = Feature(
            name="Aquatic",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is aquatic and has a swim speed equal to its walk speed. It can also breathe underwater.",
        )
        return stats, feature


Aquatic: Power = _Aquatic()

AquaticPowers: List[Power] = [Aquatic]
