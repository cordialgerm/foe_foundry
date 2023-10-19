from math import ceil
from typing import List, Tuple

import numpy as np

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_breath(candidate: BaseStatblock) -> float:
    return score(candidate, require_types=CreatureType.Dragon)


class _BreathAttack(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Breath Attack", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type or DamageType.Fire

        if stats.cr <= 3:
            distance = 15
        elif stats.cr <= 7:
            distance = 30
        elif stats.cr <= 11:
            distance = 45
        else:
            distance = 60

        if rng.random() <= 0.5:
            template = f"{distance} ft cone"
            save_type = "Constitution"
            multiplier = 4
        else:
            width = easy_multiple_of_five(5 * distance / 15)
            template = f"{2*distance} ft line {width} ft wide"
            save_type = "Dexterity"
            multiplier = 4.5

        dmg = DieFormula.target_value(
            max(5 + multiplier * 0.5 * stats.cr, multiplier * stats.cr), suggested_die=Die.d8
        )

        dc = stats.difficulty_class

        feature = Feature(
            name=f"{damage_type.capitalize()} Breath",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} breathes {damage_type} in a {template}. \
                Each creature in the area must make a DC {dc} {save_type} save. \
                On a failure, the creature takes {dmg.description} {damage_type} damage or half as much on a success.",
        )

        return stats, feature


BreathAttack: Power = _BreathAttack()

BreathPowers: List[Power] = [BreathAttack]
