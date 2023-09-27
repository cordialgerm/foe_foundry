from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
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


def _score_fearsome(
    candidate: BaseStatblock, min_cr: float = 2, supernatural: bool = True
) -> float:
    if candidate.cr < min_cr:
        return 0

    creature_types = {
        CreatureType.Dragon: HIGH_AFFINITY,
        CreatureType.Fiend: HIGH_AFFINITY,
        CreatureType.Monstrosity: MODERATE_AFFINITY,
    }

    if not supernatural:
        creature_types.update({CreatureType.Beast: LOW_AFFINITY})

    score = creature_types.get(candidate.creature_type, 0)
    if score == 0:
        return 0

    if candidate.cr >= 7:
        score += LOW_AFFINITY

    return score


def _score_horrifying(candidate: BaseStatblock, min_cr: float = 1) -> float:
    if candidate.cr < min_cr:
        return 0

    creature_types = {
        CreatureType.Aberration: HIGH_AFFINITY,
        CreatureType.Undead: EXTRA_HIGH_AFFINITY,
    }

    score = creature_types.get(candidate.creature_type, 0)
    if score == 0:
        return 0

    if candidate.cr >= 7:
        score += LOW_AFFINITY

    if candidate.secondary_damage_type == DamageType.Psychic:
        score += MODERATE_AFFINITY

    return score


class _Repulsion(Power):
    def __init__(self):
        super().__init__(name="Repulsion", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = (
            _score_horrifying(candidate) + _score_fearsome(candidate, supernatural=False)
        ) / 2
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        if _score_fearsome(stats, supernatural=False) > 0:
            name = "Fearsome Roar"
        elif _score_horrifying(stats) > 0:
            name = "Horrifying Presence"
        else:
            name = "Repulsion"

        dc = stats.difficulty_class
        feature = Feature(
            name=name,
            description=f"{stats.selfref.capitalize()} targets up to eight creatures they can see within 60 ft. Each must make a DC {dc} Charisma saving throw.\
                On a failure, the affected target is **Frightened** for 1 minute (save ends at end of turn) and must immediately use its reaction, if available, to move their speed away from {stats.selfref} \
                avoiding hazards or dangerous terrain if possible.",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
        )

        return stats, feature


class _TerrifyingVisage(Power):
    def __init__(self):
        super().__init__(name="Terrifying Visage", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_horrifying(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        aging = f"1d4 x {5 if stats.cr < 4 else 10} years"
        dc = stats.difficulty_class

        feature = Feature(
            name="Terrifying Visage",
            action=ActionType.Reaction,
            description=f"When a creature looks at {stats.selfref}, it must immediately make a DC {dc} Wisdom saving throw. \
                On a failure, the target is **Frightened** of {stats.selfref} (save ends at end of turn). \
                If the save fails by 5 or more, the target also ages {aging}. \
                A creature that succeeds on the save is immune to this effect for 1 hour.",
        )

        return stats, feature


class _DreadGaze(Power):
    def __init__(self):
        super().__init__(name="Dread Gaze", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = (
            _score_horrifying(candidate) + _score_fearsome(candidate, supernatural=True)
        ) / 2.0
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class

        feature = Feature(
            name="Dread Gaze",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 60 feet. If the target can see {stats.selfref} \
                it must succeed on a DC {dc} Wisdom save or become **Frightened** of the {stats.selfref} (save ends at end of turn). \
                If the target fails the save by 5 or more, it is also **Paralyzed** while frightened in this way. \
                A creature that succeeds on the save is immune to this effect for 1 hour.",
        )

        return stats, feature


class _MindShatteringScream(Power):
    def __init__(self):
        super().__init__(name="Mind-Shattering Scream", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_horrifying(candidate)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = DieFormula.target_value(5 + 2.5 * stats.cr, force_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Mind-Shattering Scream",
            action=ActionType.Action,
            recharge=6,
            description=f"{stats.selfref.capitalize()} releases a mind-shattering scream. All other creatures within 30 ft that can hear {stats.selfref} \
                must make a DC {dc} Intelligence saving throw. On a failure, a creature takes {dmg.description} psychic damage and is **Stunned** until the end of its next turn. \
                On a success, a creature takes half damage and is not Stunned. Creatures that are **Frightened** have disadvantage on this save.",
        )

        return stats, feature


class _NightmarishVisions(Power):
    def __init__(self):
        super().__init__(name="Nightmarish Visions", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_horrifying(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = DieFormula.target_value(max(5, 1.5 * stats.cr), force_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Nightmarish Visions",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets a creature that it can see within 30 feet and forces it to confront its deepest fears. \
                The target must succeed on a DC {dc} Wisdom save or become **Frightened** of {stats.selfref} for 1 minute (save ends at end of turn). While frightened in this way, the creature takes {dmg.description} ongoing psychic damage at the start of each of its turns.",
        )

        return stats, feature


Repulsion: Power = _Repulsion()
TerrifyingVisage: Power = _TerrifyingVisage()
DreadGaze: Power = _DreadGaze()
MindShatteringScream: Power = _MindShatteringScream()
NightmarishVisions: Power = _NightmarishVisions()

FearsomePowers: List[Power] = [
    Repulsion,
    TerrifyingVisage,
    DreadGaze,
    MindShatteringScream,
    NightmarishVisions,
]
