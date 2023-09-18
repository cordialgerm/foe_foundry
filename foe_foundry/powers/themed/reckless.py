from math import ceil
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


def _score_could_be_reckless_fighter(
    candidate: BaseStatblock, large_size_boost: bool = False, allow_defender: bool = False
) -> float:
    if not candidate.attack_type.is_melee():
        return NO_AFFINITY

    score = 0
    if ArmorClass.could_use_shield_or_wear_armor(candidate.creature_type):
        score += MODERATE_AFFINITY

    if candidate.creature_type in {
        CreatureType.Beast,
        CreatureType.Monstrosity,
    }:
        score += MODERATE_AFFINITY

    if candidate.primary_attribute_score == Stats.STR:
        score += MODERATE_AFFINITY

    if candidate.role in {MonsterRole.Bruiser, MonsterRole.Default}:
        score += MODERATE_AFFINITY

    if allow_defender and candidate.role == MonsterRole.Defender:
        score += MODERATE_AFFINITY

    if large_size_boost and candidate.size >= Size.Large:
        score += MODERATE_AFFINITY

    if candidate.attributes.WIS <= 12:
        score += MODERATE_AFFINITY

    return score if score > 0 else NO_AFFINITY


def _as_reckless_fighter(stats: BaseStatblock, uses_weapon: bool = False) -> BaseStatblock:
    new_attrs = stats.attributes.copy(primary_attribute=Stats.STR)

    changes: dict = dict(attributes=new_attrs)
    if uses_weapon:
        changes.update(attack_type=AttackType.MeleeWeapon)
    return stats.copy(**changes)


class _Charger(Power):
    def __init__(self):
        super().__init__(name="Charger", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, large_size_boost=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        dc = stats.difficulty_class
        feature = Feature(
            name="Charge",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} charges by using Dash as a bonus action. Up to one creature that is within 5 ft of the path \
                that the creature charges must make a DC {dc} Strength saving throw or be knocked Prone.",
        )
        return stats, feature


class _Frenzy(Power):
    """Frenzy (Trait). At the start of their turn, this creature can gain advantage on all melee weapon attack rolls made during this
    turn, but attack rolls against them have advantage until the start of their next turn."""

    def __init__(self):
        super().__init__(name="Frenzy", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        feature = Feature(
            name="Frenzy",
            description=f"At the start of their turn, {stats.selfref} can gain advantage on all melee weapon attack rolls made during this turn, but attack rolls against them have advantage until the start of their next turn.",
            action=ActionType.Feature,
        )
        return stats, feature


class _RefuseToSurrender(Power):
    """When this creature’s current hit points are below half their hit point maximum,
    the creature deals CR extra damage with each of their attacks."""

    def __init__(self):
        super().__init__(name="Refuse to Surrender", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(
            candidate, large_size_boost=True, allow_defender=True
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        threshold = int(ceil(stats.hp.average / 2.0))
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Refuse to Surrender",
            description=f"When {stats.selfref}'s current hit points are below {threshold}, the creature deals an extra {dmg} damage with each of its attacks.",
            action=ActionType.Feature,
        )
        return stats, feature


class _GoesDownFighting(Power):
    """When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious."""

    def __init__(self):
        super().__init__(name="Goes Down Fighting", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _WildCleave(Power):
    def __init__(self):
        super().__init__(name="Wild Cleave", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        reach = stats.attack.reach or 5 + 5
        push = 2 * reach

        feature = Feature(
            name="Wild Cleave",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes an attack against every creature within {reach} ft. On a hit, the creature is pushed up to {push} feet away.",
        )

        return stats, feature


class _FlurryOfBlows(Power):
    def __init__(self):
        super().__init__(name="Flurry of Blows", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        attacks = max(3, int(ceil(1.5 * stats.multiattack)))

        feature = Feature(
            name="Flurry of Blows",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes a reckless flurry of {attacks} attacks. Attacks against {stats.selfref} have advantage until the end of {stats.selfref}'s next turn.",
        )

        return stats, feature


Charger: Power = _Charger()
Frenzy: Power = _Frenzy()
FlurryOfBlows: Power = _FlurryOfBlows()
GoesDownFighting: Power = _GoesDownFighting()
RefuseToSurrender: Power = _RefuseToSurrender()
WildCleave: Power = _WildCleave()


RecklessPowers: List[Power] = [
    Charger,
    Frenzy,
    FlurryOfBlows,
    GoesDownFighting,
    RefuseToSurrender,
    WildCleave,
]
