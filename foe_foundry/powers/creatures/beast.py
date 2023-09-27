from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
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

    score = HIGH_AFFINITY

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

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        dc = stats.difficulty_class
        bleeding = DieFormula.target_value(0.75 * stats.attack.average_damage)
        gore_attack = stats.attack.scale(
            scalar=1.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            name="Gore",
            replaces_multiattack=2,
            additional_description=f"If {stats.selfref} moved at least 10 feet before making this attack, then the target must make a DC {dc} Dexterity saving throw. On a failure, the target is gored and suffers {bleeding.description} ongoing piercing damage at the end of each of its turns. \
                The ongoing damage ends when the creature receives magical healing, or if the creature or another creature uses an action to perform a DC 10 Medicine check",
        )

        stats = stats.add_attack(gore_attack)

        return stats, None


class _Web(Power):
    def __init__(self):
        super().__init__(name="Web", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.STR)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        stats = stats.copy(speed=new_speed)

        dc = stats.difficulty_class

        feature1 = Feature(
            name="Spider Climb",
            action=ActionType.Feature,
            description=f"{stats.selfref} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check.",
        )

        feature2 = Feature(
            name="Web Sense",
            action=ActionType.Feature,
            description=f"While in contact with a web, {stats.selfref} knows the exact location of any other creature in contact with the same web.",
        )

        feature3 = Feature(
            name="Web",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} shoots a sticky web at a point it can see within 60 feet. \
                Each creature within a 20 foot cube centered at the point must make a DC {dc} Dexterity saving throw or become **Restrained** (save ends at end of turn). \
                The area of the web is considered difficult terrain, and any creature that ends its turn in the area must repeat the save or become restrained.",
        )

        return stats, [feature1, feature2, feature3]


Gore: Power = _Gore()
HitAndRun: Power = _HitAndRun()
MotivatedByCarnage: Power = _MotivatedByCarnage()
Web: Power = _Web()

BeastPowers: List[Power] = [Gore, HitAndRun, MotivatedByCarnage, Web]
