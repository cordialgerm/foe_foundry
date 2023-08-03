from math import ceil
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


class _ShoutOrders(Power):
    def __init__(self):
        super().__init__(name="Shout Orders", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Leader:
            score += HIGH_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Intimidation):
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Persuasion):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shout Orders",
            description=f"{stats.roleref.capitalize()} chooses up to six creatures who can see and hear them. \
                          Those creatures can immediately either move their speed or make an attack.",
            action=ActionType.BonusAction,
            recharge=4,
        )
        return stats, feature


class _Intimidate(Power):
    def __init__(self):
        super().__init__(name="Intimidate", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY

        if candidate.attributes.CHA >= 15:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Intimidation):
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Persuasion):
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Intimidate",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.roleref.capitalize()} chooses a target that can hear them within 50 ft. \
                The target must make a contested Insight check against {stats.roleref}'s Intimidation. \
                On a failure, the target is Frightened of {stats.roleref} for 1 minute (save ends at end of turn).\
                While Frightened in this way, attacks made against the target have advantage.",
        )

        return stats, feature


class _Encouragement(Power):
    def __init__(self):
        super().__init__(name="Encouragement", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY

        if candidate.attributes.WIS >= 15:
            score += MODERATE_AFFINITY

        if candidate.attributes.CHA >= 15:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Insight):
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Medicine):
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Persuasion):
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attributes = stats.attributes.grant_proficiency_or_expertise(
            Skills.Medicine, Skills.Insight
        )
        stats = stats.copy(attributes=new_attributes)
        hp = int(stats.attributes.stat_mod(Stats.WIS) + max(5, ceil(stats.cr * 2)))

        feature = Feature(
            name="Encouragement",
            description=f"{stats.roleref.capitalize()} encourages another creature within 50 feet. \
                The chosen creature gains {hp} temporary hitpoints and may repeat a saving throw against any negative condition affecting them, ending that condition on a success.",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _LeadByExample(Power):
    def __init__(self):
        super().__init__(name="Lead by Example", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Leader:
            score += HIGH_AFFINITY

        if candidate.attributes.WIS >= 15:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Lead by Example",
            description=f"Whenever {stats.roleref} hits a target with an attack, any of {stats.roleref}'s allies gain advantage on attack rolls against that target \
                until the start of {stats.roleref}'s next turn.",
            action=ActionType.Feature,
        )
        return stats, feature


ShoutOrders: Power = _ShoutOrders()
Intimidate: Power = _Intimidate()
Encouragement: Power = _Encouragement()
LeadByExample: Power = _LeadByExample()


LeaderPowers: List[Power] = [ShoutOrders, Intimidate, Encouragement, LeadByExample]
