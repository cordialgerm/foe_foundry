from math import ceil
from typing import List, Tuple

import numpy as np

from ...attack_template import spell
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerBackport, PowerType
from ..power_type import PowerType
from ..scoring import score


def score_charming(candidate: BaseStatblock) -> float:
    return score(
        candidate=candidate,
        require_types=[CreatureType.Fey, CreatureType.Fiend, CreatureType.Aberration],
        require_stats=Stats.CHA,
        bonus_roles=[MonsterRole.Controller, MonsterRole.Leader],
        bonus_skills=[Skills.Deception, Skills.Persuasion],
        attack_names=spell.Gaze,
        bonus_damage=DamageType.Psychic,
        require_damage_exact_match=True,
    )


class _WordsOfTreachery(PowerBackport):
    def __init__(self):
        super().__init__(name="Words of Treachery", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_charming(candidate)

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
        return score_charming(candidate)

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
