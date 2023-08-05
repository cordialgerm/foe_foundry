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
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _PinningShot(Power):
    def __init__(self):
        super().__init__(name="Pinning Shot", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = MODERATE_AFFINITY

        if candidate.role in {MonsterRole.Controller, MonsterRole.Artillery}:
            score += MODERATE_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # TODO - modify attack action directly

        dc = stats.difficulty_class

        feature = Feature(
            name="Pinning Shot",
            action=ActionType.Feature,
            description=f"When {stats.selfref} hits with a ranged attack, the target must succeed on a DC {dc} Strength saving throw or be Restrained (save ends at end of turn).",
        )

        return stats, feature


class _Challenger(Power):
    def __init__(self):
        super().__init__(name="Challenger", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = 0

        if candidate.role == MonsterRole.Defender or ArmorClass.could_use_shield_or_wear_armor(
            candidate.creature_type
        ):
            score += HIGH_AFFINITY

        if candidate.attributes.CHA >= 18 or candidate.attributes.has_proficiency_or_expertise(
            Skills.Intimidation
        ):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Challenge Foe",
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} challenges the target to a duel. \
                The challenged target has disadvantage on attack rolls against any creature other than {stats.selfref}. \
                The target may make a DC {dc} Charisma saving throw at the end of each of its turns to end the effect.",
            action=ActionType.BonusAction,
            recharge=4,
        )
        return stats, feature


PinningShot: Power = _PinningShot()
Challenger: Power = _Challenger()

WarriorPowers: List[Power] = [PinningShot, Challenger]
