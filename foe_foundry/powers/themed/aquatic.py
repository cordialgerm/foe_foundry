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
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_aquatic(candidate: BaseStatblock) -> float:
    return score(
        candidate=candidate,
        require_types=[CreatureType.Beast, CreatureType.Monstrosity, CreatureType.Humanoid],
        bonus_damage=DamageType.Cold,
    )


class _Aquatic(PowerBackport):
    def __init__(self):
        super().__init__(name="Aquatic", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_aquatic(candidate)

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
