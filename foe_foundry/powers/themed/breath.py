from math import ceil
from typing import List, Tuple

import numpy as np

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


class _BreathAttack(Power):
    def __init__(self):
        super().__init__(name="Breath Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Dragon:
            return NO_AFFINITY

        score = HIGH_AFFINITY

        if candidate.size >= Size.Large:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type or DamageType.Fire

        if stats.cr <= 3:
            distance = 15
        elif stats.cr <= 9:
            distance = 30
        else:
            distance = 45

        if rng.random() <= 0.5:
            template = f"{distance} ft cone"
            save_type = "Constitution"
        else:
            template = f"{2*distance} ft line 5 ft wide"
            save_type = "Dexterity"

        dmg = int(ceil(max(5 + 2 * stats.cr, 4 * stats.cr)))

        dc = stats.difficulty_class

        feature = Feature(
            name=f"{damage_type.capitalize()} Breath",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} breathes {damage_type} in a {template}. \
                Each creature in the area must make a DC {dc} {save_type} save. \
                On a failure, the creature takes {dmg} {damage_type} damage or half as much on a success.",
        )

        return stats, feature


BreathAttack: Power = _BreathAttack()

BreathPowers: List[Power] = [BreathAttack]
