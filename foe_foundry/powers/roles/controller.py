from typing import List, Tuple

import numpy as np

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..attack import (
    debilitating_attack,
    flavorful_damage_types,
    flavorful_debilitating_conditions,
)
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DebilitatingAttack(Power):
    def __init__(self):
        super().__init__(name="Debilitating Attacks", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if len(flavorful_damage_types(candidate)) == 0:
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role == MonsterRole.Controller:
            score += LOW_AFFINITY

        if candidate.attack_type.is_spell():
            score += LOW_AFFINITY

        if candidate.attributes.spellcasting_mod >= 3:
            score += LOW_AFFINITY

        # "Tricky" creatures are more likely to be a PITA
        if candidate.creature_type in {
            CreatureType.Fey,
            CreatureType.Aberration,
            CreatureType.Fiend,
        }:
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        conditions = flavorful_debilitating_conditions(stats)

        i = rng.choice(len(conditions))
        condition = list(conditions)[i]

        # controllers can just automatically apply the debilitating condition because that's what they do
        stats, feature = debilitating_attack(stats, condition, save=None)

        return stats, feature


DebilitatingAttack: Power = _DebilitatingAttack()

# TODO - Controlling Spells
# TODO - Advanced Controlling Spells

ControllerPowers: List[Power] = [DebilitatingAttack]
