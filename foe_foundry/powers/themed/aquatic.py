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
from ..power import LOW_POWER, Power, PowerType, PowerWithStandardScoring
from ..scoring import score


def score_aquatic(candidate: BaseStatblock) -> float:
    return score(
        candidate=candidate,
    )


class _Aquatic(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[CreatureType.Beast, CreatureType.Monstrosity, CreatureType.Humanoid],
        )

        super().__init__(
            name="Aquatic",
            power_type=PowerType.Theme,
            source="SRD5.1 Merfolk",
            theme="Aquatic",
            power_level=LOW_POWER,
            score_args=score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(swim=stats.speed.walk)
        new_senses = stats.senses.copy(darkvision=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Aquatic",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is aquatic and has a swim speed equal to its walk speed. It can also breathe underwater.",
        )
        return [feature]


Aquatic: Power = _Aquatic()

AquaticPowers: List[Power] = [Aquatic]
