from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock) -> float:
    if candidate.creature_type != CreatureType.Plant:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _PoisonThorns(Power):
    def __init__(self):
        super().__init__(name="Poison Thorns", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class_easy

        poison_thorns = stats.attack.scale(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Poison Thorns",
            replaces_multiattack=2,
        ).split_damage(DamageType.Poison, split_ratio=0.9)

        # the ongoing bleed damage should be equal to the poison damage formula for symmetry
        # the damage threshold should be a nice easy multiple of 5 close to half the bleed damage
        bleeding_damage = (
            poison_thorns.additional_damage.formula
            if poison_thorns.additional_damage
            else DieFormula.from_expression("1d6")
        )
        threshold = easy_multiple_of_five(bleeding_damage.average / 2, max_val=20)

        bleeding = Bleeding(
            damage=bleeding_damage,
            damage_type=DamageType.Poison,
            dc=dc,
            threshold=threshold,
        )

        poison_thorns = poison_thorns.copy(
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or gain {bleeding}."
        )

        stats = stats.add_attack(poison_thorns)

        return stats, []


class _GraspingRoots(Power):
    def __init__(self):
        super().__init__(name="Grasping Roots", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Grasping Roots",
            action=ActionType.Reaction,
            description=f"When a creature attempts to leave a space within 5 feet of {stats.selfref} then it must make a DC {dc} Strength save. \
                On a failure, the creature is restrained until the start of its next turn and {stats.selfref} may also make an opportunity attack against the creature.",
        )
        return stats, feature


class _ChokingVine(Power):
    def __init__(self):
        super().__init__(name="Choking Vine", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy

        choke_attack = stats.attack.scale(
            scalar=1.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Choking Vine",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save. On a failure, the creature is **Grappled** (escape DC {dc}). \
                While grappled in this way, it cannot speak, cannot breathe, begins choking, and cannot cast spells that require a verbal component.",
        )

        stats = stats.add_attack(choke_attack)

        return stats, None


class _HypnoticSpores(Power):
    def __init__(self):
        super().__init__(name="Hypnotic Spores", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        distance = 30 if stats.difficulty_class <= 7 else 45

        feature = Feature(
            name="Hypnotic Spores",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} releases a cloud of hypnotic spores. Each non-plant creature within {distance} feet must make a DC {dc} Constitution save. \
                On a failure, the creature is **Poisoned** for 1 minute (save ends at end of turn). While poisoned in this way, the target is **Incapacitated**",
        )

        return stats, feature


class _SpikeGrowth(Power):
    def __init__(self):
        super().__init__(name="Spike Growth", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        uses = min(3, ceil(stats.cr / 5))

        feature = Feature(
            name="Spike Growth",
            action=ActionType.Action,
            uses=uses,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} releases razor-sharp thorns, creating the effect of a *Spike Growth* spell (without requiring concentration).",
        )

        return stats, feature


ChokingVine: Power = _ChokingVine()
GraspingRoots: Power = _GraspingRoots()
HypnoticSpores: Power = _HypnoticSpores()
PoisonThorns: Power = _PoisonThorns()
SpikeGrowth: Power = _SpikeGrowth()


PlantPowers: List[Power] = [
    ChokingVine,
    GraspingRoots,
    HypnoticSpores,
    PoisonThorns,
    SpikeGrowth,
]
