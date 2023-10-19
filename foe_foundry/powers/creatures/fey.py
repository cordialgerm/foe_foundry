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
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_fey(candidate: BaseStatblock) -> float:
    if candidate.creature_type != CreatureType.Fey:
        return NO_AFFINITY

    return HIGH_AFFINITY


def as_psychic_fey(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)

    return stats


def as_cursed_fey(stats: BaseStatblock) -> BaseStatblock:
    if stats.secondary_damage_type is None:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

    return stats


class _TeleportingStep(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Teleporting Step", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        distance = stats.speed.walk
        feature = Feature(
            name="Teleporting Step",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports up to {distance} feet to an unoccupied space they can see.",
        )
        return stats, feature


class _BeguilingAura(PowerBackport):
    def __init__(self):
        super().__init__(name="Beguiling Aura", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = as_psychic_fey(stats)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Beguiling Aura",
            action=ActionType.Feature,
            description=f"An enemy of {stats.selfref} who moves within 25 of them for the first time on their turn \
                or starts their turn there must succeed on a DC {dc} Wisdom saving throw or be **Charmed** by {stats.selfref} until the end of their turn.",
        )
        return stats, feature


class _NegotiateLife(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Negotiate Life", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_cursed_fey(stats)
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, suggested_die=Die.d8)
        healing = easy_multiple_of_five(
            1.75 * stats.attack.average_damage, min_val=5, max_val=45
        )
        dc = stats.difficulty_class

        feature = Feature(
            name="Negotiate Life",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} enacts a magical bargain, siphoning energy from its opponents to heal its wounds. {stats.selfref.capitalize()} targets up to three creatures it can see within 60 feet of itself. \
                Each target must make a DC {dc} Constitution saving throw, taking {dmg.description} necrotic damage on a failed save, or half as much damage on a successful one. \
                {stats.selfref.capitalize()} then regains {healing} hit points.",
        )
        return stats, feature


class _FaeCounterspell(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Fae Counterspell", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_psychic_fey(stats)
        dmg = DieFormula.target_value(0.75 * stats.attack.average_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fae Counterspell",
            action=ActionType.Reaction,
            description=f"{stats.selfref.capitalize()} attempts to interrupt a creature it can see within 60 feet \
                that is casting a spell with verbal, somatic, or material components. \
                The caster takes {dmg.description} psychic damage and must make a DC {dc} Charisma saving throw. \
                On a failed save, the spell fails and has no effect, but the casting creature is immune to this effect for 24 hours.",
        )
        return stats, feature


class _Awaken(PowerBackport):
    def __init__(self):
        super().__init__(name="Awaken", power_type=PowerType.Creature, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        if stats.cr >= 5:
            creature = "**Awakened Tree**"
            formula = DieFormula.target_value(1 + stats.cr / 4, force_die=Die.d4)
        else:
            creature = "**Awakened Shrub**"
            formula = DieFormula.target_value(3 + 4 * stats.cr, force_die=Die.d4)

        feature = Feature(
            name="Awaken",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically awakens {formula.description} {creature}. They act in initiative immediately after {stats.selfref} and obey its verbal commands (no action required).",
        )
        return stats, feature


class _FaeBargain(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Fae Bargain", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_fey(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = as_psychic_fey(stats)

        uncommon = 10
        rare = 20
        very_rare = 40
        legendary = 80
        artifact = 160
        dc = stats.difficulty_class

        feature = Feature(
            name="Fae Bargain",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} magically bargains with a creature it can see within 60 feet. The creature must make a DC {dc} Charisma save. \
                On a failure, the highest rarity magical item in that creature's possession becomes cursed and loses all magical powers and abilities and acts as a mundane item of the corresponding type. \
                {stats.selfref.capitalize()} then gains temporary hitpoints based on the rarity of the magical item: {uncommon} for an uncommon item, {rare} for a rare item, {very_rare} for a very rare item, \
                {legendary} for a legendary item and {artifact} for an artifact. This curse lasts until the fae verbally renounces the bargain, the fae is destroyed, or the curse is removed via *Remove Curse* or similar effect.",
        )
        return stats, feature


Awaken: Power = _Awaken()
BeguilingAura: Power = _BeguilingAura()
FaeBargain: Power = _FaeBargain()
FaeCounterspell: Power = _FaeCounterspell()
TeleportingStep: Power = _TeleportingStep()
NegotiateLife: Power = _NegotiateLife()

FeyPowers: List[Power] = [
    Awaken,
    BeguilingAura,
    FaeBargain,
    FaeCounterspell,
    TeleportingStep,
    NegotiateLife,
]
