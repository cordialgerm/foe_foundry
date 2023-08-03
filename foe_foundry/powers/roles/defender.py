from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _StickWithMe(Power):
    def __init__(self):
        super().__init__(name="Stick with Me!", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = 0

        if candidate.role == MonsterRole.Defender:
            score += HIGH_AFFINITY

        if candidate.ac.has_shield:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Intimidation):
            score += LOW_AFFINITY

        if ArmorClass.could_use_shield_or_wear_armor(candidate.creature_type):
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Stick with Me!",
            description=f"When {stats.selfref} hits with an attack, the target has disadvantage on attack rolls \
                against any other creature other than this one until the end of the target's next turn.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Blocker(Power):
    def __init__(self):
        super().__init__(name="Blocker", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Defender:
            score += MODERATE_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Athletics):
            score += MODERATE_AFFINITY

        if candidate.size >= Size.Large:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Blocker",
            description=f"Any creature starting their turn next to {stats.selfref} has their speed reduced by half until the end of their turn.",
            action=ActionType.Feature,
        )

        return stats, feature


StickWithMe: Power = _StickWithMe()


DefenderPowers: List[Power] = [StickWithMe]
