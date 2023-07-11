from typing import List, Tuple

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


class _HitAndRun(Power):
    def __init__(self):
        super().__init__(name="Hit and Run", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Beast:
            return NO_AFFINITY

        score = MODERATE_AFFINITY
        if candidate.primary_attribute == Stats.DEX:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        stats = stats.apply_monster_dials(dials=MonsterDials(primary_attribute=Stats.DEX))
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
        if candidate.creature_type != CreatureType.Beast:
            return NO_AFFINITY

        score = MODERATE_AFFINITY
        if candidate.primary_attribute == Stats.STR:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        stats = stats.apply_monster_dials(dials=MonsterDials(primary_attribute=Stats.STR))
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


HitAndRun: Power = _HitAndRun()
MotivatedByCarnage: Power = _MotivatedByCarnage()

BeastPowers: List[Power] = [HitAndRun, MotivatedByCarnage]

# Empowered by Carnage (Reaction). When this creature hits
# another creature with a melee attack and the damage from the
# attack reduces the target below half its hit points or to 0 hit
# points, this creature can immediately move up to their speed
# and repeat the melee attack against another target.

# This reaction captures the ferocious nature of the beast,
# motivated by seeing prey take a grievous wound or meet
# their end.
