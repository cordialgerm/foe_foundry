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
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Repulsion(Power):
    def __init__(self):
        super().__init__(name="Repulsion", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        creature_type_scores = {
            CreatureType.Aberration: HIGH_AFFINITY,
            CreatureType.Dragon: HIGH_AFFINITY,
            CreatureType.Fiend: HIGH_AFFINITY,
            CreatureType.Monstrosity: MODERATE_AFFINITY,
            CreatureType.Beast: LOW_AFFINITY,
        }

        if candidate.creature_type not in creature_type_scores:
            return NO_AFFINITY

        score = creature_type_scores[candidate.creature_type]

        if candidate.cr >= 7:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        if stats.creature_type in {CreatureType.Aberration}:
            name = "Otherworldy Repulsion"
        elif stats.creature_type in {CreatureType.Dragon, CreatureType.Fiend}:
            name = "Fearsome Presence"
        elif stats.creature_type in {CreatureType.Monstrosity, CreatureType.Beast}:
            name = "Feasome Roar"
        else:
            name = "Repulsion"

        dc = stats.difficulty_class
        feature = Feature(
            name=name,
            description=f"{stats.selfref.capitalize()} targets up to eight creatures they can see within 50 ft. Each must make a DC {dc} Charisma saving throw.\
                On a failure, the affected target is Frightened (save ends at end of turn) and must immediately use its reaction, if available, to move their speed away from {stats.selfref} \
                avoiding hazards or dangerous terrain if possible.",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
        )

        return stats, feature


Repulsion: Power = _Repulsion()

FearsomePowers: List[Power] = [Repulsion]
