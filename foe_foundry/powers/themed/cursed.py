from math import ceil
from typing import List, Tuple

from numpy.random import Generator

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


class _DevilsSight(Power):
    def __init__(self):
        super().__init__(name="Devil's Sight", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.creature_type == CreatureType.Fiend:
            score += EXTRA_HIGH_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        stats = stats.copy(creature_type=CreatureType.Fiend)

        level = 2 if stats.cr <= 5 else 4

        devils_sight = Feature(
            name="Devil's Sight",
            action=ActionType.Feature,
            description=f"Magical darkness doesn't impede {stats.selfref}'s darkvision, and it can see through Hellish Darkness.",
        )

        darkness = Feature(
            name="Hellish Darkness",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref} causes shadowy black flames to fill a 15-foot radius sphere with obscuring darkness centered at a point within 60 feet that {stats.selfref} can see. \
                The darkness spreads around corners. Creatures without Devil's Sight can't see through this darkness and nonmagical light can't illuminate it. \
                If any of this spell's area overlaps with an area of light created by a spell of level {level} or lower, the spell that created the light is dispelled. \
                Hostile creatures of {stats.selfref}'s lose any resistance to fire damage while in the darkness, and immunity to fire damage is instead treated as resistance to fire damage.",
        )

        return stats, [devils_sight, darkness]


class _Despair:
    pass


class _CursedWound:
    pass


DevilsSight: Power = _DevilsSight()

CursedPowers: List[Power] = [DevilsSight]
