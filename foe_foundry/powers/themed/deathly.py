from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score(candidate: BaseStatblock, undead_only: bool = False) -> float:
    score = 0

    if candidate.creature_type == CreatureType.Undead:
        score += HIGH_AFFINITY

    if not undead_only and candidate.creature_type == CreatureType.Fiend:
        score += MODERATE_AFFINITY

    if candidate.secondary_damage_type == DamageType.Necrotic:
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _AuraOfDoom(Power):
    def __init__(self):
        super().__init__(name="Aura of Doom", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 30 if stats.cr <= 7 else 50

        feature = Feature(
            name="Aura of Doom",
            description=f"Each enemy within {distance} ft of {stats.selfref} who makes a death saving throw does so at disadvantage.",
            action=ActionType.Feature,
        )

        return stats, feature


class _AuraOfAnnihilation(Power):
    def __init__(self):
        super().__init__(name="Aura of Annihilation", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 5 if stats.cr <= 11 else 10
        dmg = int(floor(max(5 + stats.cr, 1.5 * stats.cr)))
        dc = stats.difficulty_class_easy
        qualifier = f"non-{stats.creature_type.lower()}"

        feature = Feature(
            name="Aura of Annihilation",
            description=f"Each {qualifier} creature that ends its turn within {distance} ft of {stats.selfref} must make a DC {dc} Constitution saving throw. \
                On a failure, they take {dmg} necrotic damage and gain one Death Save failure. With three failures, a creature dies. \
                On a success, a creature takes half damage and does not gain a Death Save failure. With three successes, a creature is immune to this effect",
            action=ActionType.Feature,
        )

        return stats, feature


class _UndyingMinions(Power):
    def __init__(self):
        super().__init__(name="Undying Minions", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Undying Minions",
            description=f"When a non-zombie ally who can see {stats.selfref} is reduced to 0 hp, that ally immediately becomes a zombie (retaining its current stats). \
                The ally gains the Undead type and stands up with 1 hit point. If damage reduces the zombie to 0 hit points, it may make a DC 15 Constitution saving throw. \
                On a success, the zombie drops to 1 hit point instead.",
            action=ActionType.Feature,
        )

        return stats, feature


class _WitheringBlow(Power):
    def __init__(self):
        super().__init__(name="Withering Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        dmg = int(floor(3 + stats.cr))

        feature = Feature(
            name="Withering Blow",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting with an attack, the target takes an additional {dmg} ongoing necrotic damage at the start of each of their turns. \
                The effect can be ended by any character using an action to perform a DC {dc} Medicine check or if the target receives {dmg} or more points of magical healing in a round.",
        )

        return stats, feature


class _DrainingBlow(Power):
    def __init__(self):
        super().__init__(name="Draining Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        feature = Feature(
            name="Draining Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, the {stats.selfref} converts all of that attack's damage to necrotic damage and {stats.selfref} regains hit points equal to the necrotic damage dealt.",
        )

        return stats, feature


class _ShadowStride(Power):
    def __init__(self):
        super().__init__(name="Shadow Stride", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, undead_only=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shadow Stride",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports from one source of shadows to another that it can see within 60 feet.",
        )

        return stats, feature


class _FleshPuppets(Power):
    def __init__(self):
        super().__init__(name="Flesh Puppets", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, undead_only=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        cr = int(ceil(stats.cr / 3))

        feature = Feature(
            name="Flesh Puppets",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} uses dark necromancy to resurrect the corpse of a nearby creature of CR {cr} or less. \
                The creature acts in initiative immediately after {stats.selfref} and obeys the commands of {stats.selfref} (no action required). \
                The flesh puppet has the same statistics as when the creature was living except it is now Undead, or uses the statistics of a **Skeleton**, **Zombie**, or **Ghoul**. \
                When the flesh puppet dies, the corpse is mangled beyond repair and is turned into a pile of viscera.",
        )

        return stats, feature


class _DevourSoul(Power):
    def __init__(self):
        super().__init__(name="Devour Soul", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate, undead_only=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = int(ceil(1.5 * stats.attack.average_damage))
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Devour Soul",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 30 feet of it that is not a Construct or an Undead. \
                The creature must succeed on a DC {dc} Charisma saving throw or take {dmg} necrotic damage. \
                If this damage reduces the target to 0 hit points, it dies and immediately rises as a **Ghoul** under {stats.selfref}'s control.",
        )

        return stats, feature


AuraOfDoom: Power = _AuraOfDoom()
AuraOfAnnihilation: Power = _AuraOfAnnihilation()
DevourSoul: Power = _DevourSoul()
DrainingBlow: Power = _DrainingBlow()
FleshPuppets: Power = _FleshPuppets()
ShadowStride: Power = _ShadowStride()
UndyingMinions: Power = _UndyingMinions()
WitheringBlow: Power = _WitheringBlow()

DeathlyPowers: List[Power] = [
    AuraOfDoom,
    AuraOfAnnihilation,
    DevourSoul,
    DrainingBlow,
    FleshPuppets,
    ShadowStride,
    UndyingMinions,
    WitheringBlow,
]
