from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Fatigue, Frozen
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
    if candidate.creature_type != CreatureType.Undead:
        return NO_AFFINITY

    return HIGH_AFFINITY


class _UndeadResilience(Power):
    def __init__(self):
        super().__init__(name="Undead Resilience", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Undead Resilience",
            action=ActionType.Reaction,
            description=f"When damage reduces {stats.selfref} to 0 hit points, it must make a Constitution saving throw with a DC of 2 + the damage taken, \
                unless the damage is radiant or from a critical hit. On a success, {stats.selfref} instead drops to 1 hit point.",
        )
        return stats, feature


class _StenchOfDeath(Power):
    def __init__(self):
        super().__init__(name="Stench of Death", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Stench of Death",
            action=ActionType.Feature,
            description=f"Any creature that starts its turn within 10 feet of {stats.selfref} must make a DC {dc} Constitution saving throw or become poisoned until the start of their next turn. \
                On a successful saving throw, the creature is immune to {stats.selfref}'s stench for 24 hours.",
        )
        return stats, feature


class _StygianBurst(Power):
    def __init__(self):
        super().__init__(name="Stygian Burst", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(0.75 * stats.attack.average_damage, force_die=Die.d8)
        frozen = Frozen(dc=dc)
        hp = easy_multiple_of_five(stats.hp.average / 2)
        distance = easy_multiple_of_five(2.5 * stats.cr, min_val=10, max_val=40)

        # to combo with the Frozen debuff
        stats = stats.copy(
            primary_damage_type=DamageType.Bludgeoning, secondary_damage_type=DamageType.Cold
        )

        feature = Feature(
            name="Stygian Burst",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} takes a critical hit, or when it is reduced to {hp} hitpoints or fewer, it releases a burst of deathly cold. \
                Each non-undead creature within {distance} feet must make a DC {dc} Consitution saving throw. On a failure, the creature takes {dmg.description} cold damage and is {frozen}",
        )

        return stats, feature


class _Frostbite(Power):
    def __init__(self):
        super().__init__(name="Frostbite", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, force_die=Die.d8)
        frozen = Frozen(dc=dc)

        stats = stats.copy(secondary_damage_type=DamageType.Cold)

        feature = Feature(
            name="Frostbite",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} causes numbing frost to form on one creature within 60 feet. The target must make a DC {dc} Constitution saving throw. \
                On a failure, it suffers {dmg.description} cold damage and is {frozen}. On a success, it suffers half damage instead.",
        )
        return stats, feature


class _SoulChill(Power):
    def __init__(self):
        super().__init__(name="Soul Chill", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        fatigue = Fatigue()
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 10, min_val=15, max_val=60)

        stats = stats.copy(secondary_damage_type=DamageType.Cold)

        feature = Feature(
            name="Soul Chill",
            action=ActionType.Reaction,
            description=f"Whenever a creature within {distance} feet that {stats.selfref} can see fails a saving throw, {stats.selfref} can attempt to leech away a portion of its spirit. \
                The creature must succeed on a DC {dc} Charisma saving throw. On a failure, it gains one level of {fatigue}.",
        )
        return stats, feature


class _SoulTether(Power):
    def __init__(self):
        super().__init__(name="Soul Tether", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Soul Tether",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 30 feet of it. A crackling cord of negative energy tethers {stats.selfref} to the target. \
                Whenever {stats.selfref} takes damage, the target must succeed on a DC {dc} Constitution saving throw. On a failed save, {stats.selfref} takes half the damage (rounded down) and the target takes the remaining. \
                The tether lasts until the beginning of {stats.selfref}'s next turn.",
        )

        return stats, feature


class _AntithesisOfLife(Power):
    def __init__(self):
        super().__init__(name="Antithesis of Life", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Antithesis of Life",
            action=ActionType.Feature,
            description=f"Whenever a creature within 30 feet of the {stats.selfref} regains hit points, it must make a DC {dc} Charisma saving throw. \
                On a failure, the healing received is reduced to zero. On a success, the creature is immune to this effect for 1 hour.",
        )
        return stats, feature


AntithesisOfLife: Power = _AntithesisOfLife()
Frostbite: Power = _Frostbite()
SoulChill: Power = _SoulChill()
SoulTether: Power = _SoulTether()
StenchOfDeath: Power = _StenchOfDeath()
StygianBurst: Power = _StygianBurst()
UndeadResilience: Power = _UndeadResilience()

UndeadPowers: List[Power] = [
    AntithesisOfLife,
    Frostbite,
    SoulChill,
    SoulTether,
    StenchOfDeath,
    StygianBurst,
    UndeadResilience,
]
