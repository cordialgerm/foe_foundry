from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Burning, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_psychic(candidate: BaseStatblock) -> float:
    # this is great for aberrations, psychic focused creatures, and controllers
    score = 0

    if candidate.creature_type == CreatureType.Aberration:
        score += HIGH_AFFINITY
    if candidate.secondary_damage_type == DamageType.Psychic:
        score += HIGH_AFFINITY
    if candidate.role == MonsterRole.Controller:
        score += MODERATE_AFFINITY
    return score if score > 0 else NO_AFFINITY


def as_psychic(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)
    return stats


class _Telekinetic(Power):
    """This creature chooses one creature they can see within 100 feet of them
    weighing less than 400 pounds. The target must succeed on a Strength saving throw
    (DC = 11 + 1/2 CR) or be pulled up to 80 feet directly toward this creature."""

    def __init__(self):
        super().__init__(name="Telekinetic", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_psychic(stats)

        dc = int(ceil(11 + stats.cr / 2.0))

        feature = Feature(
            name="Telekinetic Grasp",
            description=f"{stats.selfref.capitalize()} chooses one creature they can see within 100 feet weighting less than 400 pounds. \
                The target must succeed on a DC {dc} Strength saving throw or be pulled up to 80 feet directly toward {stats.selfref}",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _PsychicInfestation(Power):
    def __init__(self):
        super().__init__(name="Psychic Infestation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_psychic(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_psychic(stats)

        distance = easy_multiple_of_five(30 + 5 * stats.cr, min_val=30, max_val=90)
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(
            target=1.5 * stats.attack.average_damage, force_die=Die.d6
        )
        burning = Burning(
            damage=DieFormula.from_dice(d6=dmg.n_die // 2), damage_type=DamageType.Psychic
        )

        feature = Feature(
            name="Psychic Infestation",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} attempts to infect the mind of a creature it can see within {distance} feet. \
                The creature must make a DC {dc} Intelligence save. On a failure, it takes {dmg.description} psychic damage and is {burning.caption}. \
                On a success, it takes half damage instead. {burning.description_3rd}",
        )

        return stats, feature


PsychicInfestation: Power = _PsychicInfestation()
Telekinetic: Power = _Telekinetic()

PsychicPowers: List[Power] = [PsychicInfestation, Telekinetic]
