from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
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


def score_ambusher(candidate: BaseStatblock, speed_boost: bool = False) -> float:
    if candidate.role != MonsterRole.Ambusher:
        return NO_AFFINITY

    score = HIGH_AFFINITY

    if candidate.primary_attribute == Stats.DEX:
        score += LOW_AFFINITY

    if candidate.attributes.has_proficiency_or_expertise(Skills.Deception):
        score += MODERATE_AFFINITY

    if speed_boost and candidate.speed.walk >= 40:
        score += MODERATE_AFFINITY

    if score == 0:
        return NO_AFFINITY
    else:
        return score


def as_ambusher(stats: BaseStatblock) -> BaseStatblock:
    new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
    stats = stats.copy(attributes=new_attrs)
    return stats


class _DistractingAttack(Power):
    def __init__(self):
        super().__init__(name="Distracting Attack", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ambusher(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_ambusher(stats)

        feature = Feature(
            name="Distracting Attack",
            action=ActionType.Feature,
            description=f"On a hit, {stats.roleref} can choose to become **Invisible** until the start of their next turn or the next time they make an attack or cast a spell.",
            hidden=True,
            modifies_attack=True,
        )

        return stats, feature


class _ShadowyMovement(Power):
    def __init__(self):
        super().__init__(name="Shadowy Movement", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ambusher(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_ambusher(stats)

        feature = Feature(
            name="Shadowy Movement",
            description=f"{stats.roleref.capitalize()} can attempt to hide in dim light or lightly obscured terrain. \
            When {stats.roleref} moves, they can make a Dexterity (Stealth) check to hide as part of that movement",
            action=ActionType.Feature,
        )

        return stats, feature


class _DeadlyAmbusher(Power):
    def __init__(self):
        super().__init__(name="Deadly Ambusher", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ambusher(candidate, speed_boost=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_ambusher(stats)

        feature = Feature(
            name="Deadly Ambusher",
            description=f"{stats.selfref.capitalize()} has advantage on initiative rolls. \
                On the first turn of combat, it has advantage on any attack rolls against targets with lower initiative than it, \
                and it scores a critical hit on a score of 19 or 20.",
            action=ActionType.Feature,
        )

        return stats, feature


class _DeadlyPrecision(Power):
    def __init__(self):
        super().__init__(name="Deadly Precision", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ambusher(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = as_ambusher(stats)
        dmg = DieFormula.target_value(2 + 0.5 * stats.cr, force_die=Die.d6)
        feature = Feature(
            name="Deadly Precision",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"If the attack was made with advantage, it deals an additional {dmg.description} damage",
        )
        return stats, feature


DeadlyPrecision: Power = _DeadlyPrecision()
DistractingAttack: Power = _DistractingAttack()
ShadowyMovement: Power = _ShadowyMovement()
DeadlyAmbusher: Power = _DeadlyAmbusher()

AmbusherPowers: List[Power] = [
    DeadlyPrecision,
    DistractingAttack,
    ShadowyMovement,
    DeadlyAmbusher,
]
