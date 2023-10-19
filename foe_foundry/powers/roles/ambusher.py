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
from ..power import Power, PowerBackport, PowerType
from ..utils import score


def score_ambusher(candidate: BaseStatblock, speed_boost: bool = False) -> float:
    return score(
        candidate=candidate,
        require_roles=MonsterRole.Ambusher,
        bonus_stats=Stats.DEX,
        bonus_skills=Skills.Stealth,
        bonus_speed=40,
    )


def as_ambusher(stats: BaseStatblock) -> BaseStatblock:
    new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
    stats = stats.copy(attributes=new_attrs)
    return stats


class _DistractingAttack(PowerBackport):
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


class _ShadowyMovement(PowerBackport):
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


class _DeadlyAmbusher(PowerBackport):
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


DistractingAttack: Power = _DistractingAttack()
ShadowyMovement: Power = _ShadowyMovement()
DeadlyAmbusher: Power = _DeadlyAmbusher()

AmbusherPowers: List[Power] = [
    DistractingAttack,
    ShadowyMovement,
    DeadlyAmbusher,
]
