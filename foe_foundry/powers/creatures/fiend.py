from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_fiend(candidate: BaseStatblock, min_cr: float | None = None) -> float:
    if candidate.creature_type != CreatureType.Fiend:
        return NO_AFFINITY
    if min_cr is not None and candidate.cr < min_cr:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _EmpoweredByDeath(Power):
    def __init__(self):
        super().__init__(name="Empowered by Death", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        hp = int(floor(5 + 2 * stats.cr))

        feature = Feature(
            name="Empowered by Death",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp whenever a creature dies within 30 ft. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        return stats, feature


class _RelishYourFailure(Power):
    def __init__(self):
        super().__init__(name="Relish Your Failure", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        hp = DieFormula.target_value(max(2, stats.cr / 2), suggested_die=Die.d4)
        dc = stats.difficulty_class
        feature1 = Feature(
            name="Relish Your Failure",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp.description} hp whenever a creature fails a saving throw within 60 feet. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        feature2 = Feature(
            name="Fiendish Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} casts the *Bane* spell (spell save DC {dc}) at 2nd level, targeting up to 4 creatures, and without requiring concentration.",
        )

        return stats, [feature1, feature2]


class _FiendishTeleporation(Power):
    def __init__(self):
        super().__init__(name="Fiendish Teleportation", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        multiplier = 1.5 if stats.multiattack >= 2 else 0.75
        dmg = DieFormula.target_value(
            multiplier * stats.attack.average_damage, force_die=Die.d10
        )
        distance = easy_multiple_of_five(stats.cr * 10, min_val=30, max_val=120)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fiendish Teleportation",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} disappears and reappars in a burst of flame. It teleports up to {distance} feet to an unoccupied location it can see. \
                Each other creature within 10 feet of {stats.selfref} either before or after it teleports must make a DC {dc} Dexterity saving throw. On a failure, it takes {dmg.description} fire damage.",
        )
        return stats, feature


class _WallOfFire(Power):
    def __init__(self):
        super().__init__(name="Wall of Fire", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, min_cr=5)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy

        if stats.cr <= 5:
            uses = 1
            concentration = ""
        elif stats.cr <= 10:
            uses = 3
            concentration = " without requiring concentration"
        else:
            uses = None
            concentration = " without requiring concentration"

        feature = Feature(
            name="Wall of Fire",
            action=ActionType.Action,
            replaces_multiattack=2,
            uses=uses,
            description=f"{stats.selfref.capitalize()} magically casts the *Wall of Fire* spell (spell save DC {dc}){concentration}.",
        )
        return stats, feature


class _FiendishBite(Power):
    def __init__(self):
        super().__init__(name="Fiendish Bite", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class

        bite_attack = stats.attack.scale(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            name="Fiendish Bite",
            die=Die.d6,
            attack_type=AttackType.MeleeNatural,
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become **Poisoned** for 1 minute (save ends at end of turn).",
        ).split_damage(DamageType.Poison, split_ratio=0.9)

        stats = stats.add_attack(bite_attack)

        return stats, []


class _FiendishSummons(Power):
    def __init__(self):
        super().__init__(name="Fiendish Summons", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, min_cr=3)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        _, _, description = summoning.determine_summon_formula(
            summon_list=summoning.Fiends, summon_cr_target=stats.cr / 2.5, rng=rng
        )

        feature = Feature(
            name="Fiendish Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} summons forth additional fiendish allies. {description}",
        )

        return stats, feature


EmpoweredByDeath: Power = _EmpoweredByDeath()
FiendishBite: Power = _FiendishBite()
FiendishSummons: Power = _FiendishSummons()
FiendishTeleportation: Power = _FiendishTeleporation()
RelishYourFailure: Power = _RelishYourFailure()
WallOfFire: Power = _WallOfFire()

FiendishPowers: List[Power] = [
    EmpoweredByDeath,
    FiendishBite,
    FiendishSummons,
    FiendishTeleportation,
    RelishYourFailure,
    WallOfFire,
]
