from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _WordsOfTreachery(PowerBackport):
    def __init__(self):
        super().__init__(name="Words of Treachery", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        creature_types = {
            CreatureType.Fey: EXTRA_HIGH_AFFINITY,
            CreatureType.Fiend: MODERATE_AFFINITY,
            CreatureType.Aberration: LOW_AFFINITY,
        }

        roles = {
            MonsterRole.Controller: MODERATE_AFFINITY,
            MonsterRole.Leader: MODERATE_AFFINITY,
        }

        score = creature_types.get(candidate.creature_type, 0) + roles.get(candidate.role, 0)

        if candidate.attributes.has_proficiency_or_expertise(Skills.Deception):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 20 if stats.cr <= 4 else 40
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Words of Treachery",
            description=f"{stats.selfref.capitalize()} speaks deceitful words at a target within {distance} ft of them who can see and hear them. \
                The target must succeed on a DC {dc} Charisma saving throw or use their reaction to move up to half their speed and make a melee, ranged, or cantrip attack against a target of {stats.selfref}'s choice. \
                This counts as a **Charm** effect.",
            action=ActionType.Action,
            replaces_multiattack=1,
        )

        return stats, feature


class _CharmingWords(PowerBackport):
    def __init__(self):
        super().__init__(name="Charming Words", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        creature_types = {
            CreatureType.Fey: EXTRA_HIGH_AFFINITY,
            CreatureType.Fiend: MODERATE_AFFINITY,
            CreatureType.Dragon: MODERATE_AFFINITY,
        }

        roles = {
            MonsterRole.Controller: MODERATE_AFFINITY,
            MonsterRole.Leader: MODERATE_AFFINITY,
        }

        score = creature_types.get(candidate.creature_type, 0) + roles.get(candidate.role, 0)

        if candidate.attributes.has_proficiency_or_expertise(Skills.Persuasion):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 60 if stats.cr <= 7 else 90
        dc = stats.difficulty_class

        feature = Feature(
            name="Charming Words",
            description=f"{stats.selfref.capitalize()} chooses any number of targets within {distance} ft that can hear them. \
                Each target must succeed on a DC {dc} Charisma saving throw or be **Charmed** by {stats.selfref} until the end of their next turn.",
            action=ActionType.BonusAction,
            recharge=5,
        )

        return stats, feature


WordsOfTreachery: Power = _WordsOfTreachery()
CharmingWords: Power = _CharmingWords()

CharmPowers: List[Power] = [WordsOfTreachery, CharmingWords]
