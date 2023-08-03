from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
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


class _NimbleReaction(Power):
    def __init__(self):
        super().__init__(name="Nimble Reaction", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Acrobatics):
            score += HIGH_AFFINITY

        if candidate.speed.fastest_speed >= 40:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Acrobatics)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Nimble Reaction",
            action=ActionType.Reaction,
            description=f"When the {stats.selfref} is the only target of a melee attack, they can move up to their speed without provoking opportunity attacks.\
                If this movement leaves the {stats.selfref} outside the attacking creature's reach, then the attack misses.",
            recharge=4,
        )

        return stats, feature


NimbleReaction: Power = _NimbleReaction()
