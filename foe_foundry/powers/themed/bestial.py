from math import ceil
from typing import List, Tuple

import numpy as np

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_bestial(candidate: BaseStatblock, **kwargs) -> float:
    args: dict = dict(
        candidate=candidate,
        require_types=[CreatureType.Monstrosity, CreatureType.Beast, CreatureType.Dragon],
        bonus_roles=MonsterRole.Bruiser,
    )
    args.update(kwargs)
    return score(**args)


class _EarthshakingDemise(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Earthshaking Demise", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_bestial(candidate, bonus_size=Size.Huge)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Earthshaking Demise",
            description=f"When {stats.selfref} dies, they topple to the ground, forcing each smaller creature within 20 feet to succeed on a DC 15 Strength saving throw or be knocked **Prone**.",
            action=ActionType.Reaction,
        )

        return stats, feature


class _FeralRetaliation(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Feral Retaliation", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_bestial(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        hp = easy_multiple_of_five(stats.hp.average / 2, min_val=5)

        feature = Feature(
            name="Feral Retaliation",
            description=f"When {stats.selfref} is hit by an attack, they can make an opportunity attack against the attacker. If {stats.selfref} is below {hp} hp then the attack is made with advantage.",
            action=ActionType.Reaction,
        )

        return stats, feature


EarthshakingDemise: Power = _EarthshakingDemise()
FeralRetaliation: Power = _FeralRetaliation()

BestialPowers: List[Power] = [EarthshakingDemise, FeralRetaliation]
