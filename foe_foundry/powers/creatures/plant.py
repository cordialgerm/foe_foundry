from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Bleeding, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerBackport, PowerType
from ..scoring import score


def score_plant(candidate: BaseStatblock, **args) -> float:
    return score(candidate=candidate, require_types=CreatureType.Plant, **args)


class _PoisonThorns(PowerBackport):
    def __init__(self):
        super().__init__(name="Poison Thorns", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_plant(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class_easy

        def customize(a: Attack) -> Attack:
            a = a.split_damage(DamageType.Poison, split_ratio=0.9)

            # the ongoing bleed damage should be equal to the poison damage formula for symmetry
            # the damage threshold should be a nice easy multiple of 5 close to half the bleed damage
            bleeding_damage = (
                a.additional_damage.formula
                if a.additional_damage
                else DieFormula.from_expression("1d6")
            )
            threshold = easy_multiple_of_five(bleeding_damage.average / 2, max_val=20)

            bleeding = Bleeding(
                damage=bleeding_damage,
                damage_type=DamageType.Poison,
                dc=dc,
                threshold=threshold,
            )

            a = a.copy(
                additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or gain {bleeding}."
            )
            return a

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Poison Thorns",
            replaces_multiattack=2,
            callback=customize,
        )

        return stats, []


class _GraspingRoots(PowerBackport):
    def __init__(self):
        super().__init__(name="Grasping Roots", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_plant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Grasping Roots",
            action=ActionType.Reaction,
            description=f"When a creature attempts to leave a space within 5 feet of {stats.selfref} then it must make a DC {dc} Strength save. \
                On a failure, the creature is restrained until the start of its next turn and {stats.selfref} may also make an opportunity attack against the creature.",
        )
        return stats, feature


class _ChokingVine(PowerBackport):
    def __init__(self):
        super().__init__(name="Choking Vine", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_plant(candidate, require_attack_types=AttackType.AllRanged())

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy

        stats = stats.add_attack(
            scalar=1.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Choking Vine",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save. On a failure, the creature is **Grappled** (escape DC {dc}). \
                While grappled in this way, it cannot speak, cannot breathe, begins choking, and cannot cast spells that require a verbal component.",
        )

        return stats, None


class _HypnoticSpores(PowerBackport):
    def __init__(self):
        super().__init__(name="Hypnotic Spores", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_plant(candidate)

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


class _SpikeGrowth(PowerBackport):
    def __init__(self):
        super().__init__(name="Spike Growth", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_plant(candidate)

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
