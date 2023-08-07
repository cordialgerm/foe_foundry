from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
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


class _EarthshakingDemise(Power):
    def __init__(self):
        super().__init__(name="Earthsaking Demise", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.size < Size.Huge:
            return NO_AFFINITY

        score = LOW_AFFINITY

        creature_types = {
            CreatureType.Giant: EXTRA_HIGH_AFFINITY,
            CreatureType.Monstrosity: HIGH_AFFINITY,
            CreatureType.Beast: MODERATE_AFFINITY,
            CreatureType.Construct: MODERATE_AFFINITY,
            CreatureType.Elemental: LOW_AFFINITY,
            CreatureType.Dragon: LOW_AFFINITY,
        }

        score += creature_types.get(candidate.creature_type, 0)

        if candidate.role in {MonsterRole.Bruiser}:
            score += LOW_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Earthshaking Demise",
            description=f"When {stats.selfref} dies, they topple to the ground, forcing each smaller creature within 20 feet to succeed on a DC 15 Strength saving throw or be knocked Prone.",
            action=ActionType.Reaction,
        )

        return stats, feature


class _FeralRetaliation(Power):
    def __init__(self):
        super().__init__(name="Feral Retaliation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        creature_types = {
            CreatureType.Beast: HIGH_AFFINITY,
            CreatureType.Monstrosity: HIGH_AFFINITY,
            CreatureType.Giant: MODERATE_AFFINITY,
            CreatureType.Dragon: LOW_AFFINITY,
        }

        score += creature_types.get(candidate.creature_type, 0)

        if candidate.role in {MonsterRole.Bruiser}:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        hp = int(ceil(stats.hp.average / 2))

        feature = Feature(
            name="Feral Retaliation",
            description=f"When {stats.selfref} is hit by an attack, they can make an opportunity attack against the attacker. If {stats.selfref} is below {hp} then the attack is made with advantage.",
            action=ActionType.Reaction,
        )

        return stats, feature


EarthshakingDemise: Power = _EarthshakingDemise()
FeralRetaliation: Power = _FeralRetaliation()

BestialPowers: List[Power] = [EarthshakingDemise, FeralRetaliation]
