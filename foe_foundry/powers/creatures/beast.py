from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_beast(candidate: BaseStatblock, primary_attribute: Stats | None = None) -> float:
    if candidate.creature_type != CreatureType.Beast:
        return NO_AFFINITY

    score = MODERATE_AFFINITY

    if primary_attribute is not None and candidate.primary_attribute == primary_attribute:
        score += MODERATE_AFFINITY
    return score


class _HitAndRun(Power):
    def __init__(self):
        super().__init__(name="Hit and Run", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.DEX)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Hit and Run",
            action=ActionType.BonusAction,
            description="This creature moves up to 30 feet without provoking opportunity attacks. \
                If it ends its movement behind cover or in an obscured area, it can make a Stealth check to hide.",
        )

        return stats, feature


class _MotivatedByCarnage(Power):
    def __init__(self):
        super().__init__(name="Motivated by Carnage", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.STR)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Survival)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Motivated by Carnage",
            action=ActionType.Reaction,
            description="When this creature reduces another target to below half its hit points or to 0 hit points, \
                         this creature can immediately move up to its speed and make a melee attack against another target. \
                         This Reaction can only activate once per target.",
        )

        return stats, feature


class _Gore(Power):
    def __init__(self):
        super().__init__(name="Gore", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.STR)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = int(ceil(0.75 * stats.attack.average_damage))

        feature = Feature(
            name="Gore",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} moves up to its speed and then makes an attack. On a hit, the target is gored and suffers {dmg} ongoing piercing damage at the end of each of its turns. \
                The ongoing damage ends when the creature receives magical healing, or if the creature or another creature uses an action to perform a DC 10 Medicine check",
        )

        return stats, feature


Gore: Power = _Gore()
HitAndRun: Power = _HitAndRun()
MotivatedByCarnage: Power = _MotivatedByCarnage()

BeastPowers: List[Power] = [Gore, HitAndRun, MotivatedByCarnage]
