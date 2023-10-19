from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, spell, weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerBackport, PowerType
from ..utils import score


class _Evasion(PowerBackport):
    def __init__(self):
        super().__init__(name="Poisoning Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_stats=Stats.DEX,
            stat_threshold=14,
            bonus_roles=[MonsterRole.Ambusher, MonsterRole.Skirmisher],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Evasion",
            action=ActionType.Feature,
            description=f"If {stats.roleref} is subjected to an effect that allows it to make a Dexterity saving throw \
            to take only half damage, {stats.roleref} instead only takes half damage if it succeeds on the saving throw, \
            and only half damage if it fails.",
        )

        return stats, feature


Evasion: Power = _Evasion()

FastPowers: List[Power] = [Evasion]
