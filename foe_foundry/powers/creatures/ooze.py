from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def score_ooze(candidate: BaseStatblock, attack_modifiers: AttackModifiers = None) -> float:
    if candidate.creature_type != CreatureType.Ooze:
        return NO_AFFINITY

    score = HIGH_AFFINITY
    score += resolve_attack_modifier(candidate, attack_modifiers)
    return score if score > 0 else NO_AFFINITY


def malleable_form(stats: BaseStatblock) -> Feature:
    size = stats.size.decrement().decrement()
    return Feature(
        name="Malleable Form",
        action=ActionType.Feature,
        description=f"{stats.selfref.capitalize()} has advantage on checks to begin or escape a grapple, \
                and can move through a space as if {stats.selfref} were {size} without squeezing.",
    )


class _OozingPassage(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Oozing Passage", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_ooze(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        size = stats.size
        dc = stats.difficulty_class
        feature = Feature(
            name="Oozing Passage",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can move through the space of other creatures of size {size} or smaller \
                without provoking opportunity attacks. When {stats.selfref} does so, each creature {stats.selfref} moves through must succed on a \
                DC {dc} Strength save or be restrained until the end of their next turn.",
        )
        return stats, [malleable_form(stats), feature]


class _ElongatedLimbs(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Elongated Limbs", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY
        return score_ooze(candidate, attack_modifiers=natural.Slam)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        feature = Feature(
            name="Elongated Limbs",
            action=ActionType.Reaction,
            description=f"{stats.selfref.capitalize()} may make an opportunity attack whenever a creature moves in or out of {stats.selfref}'s reach.",
        )
        new_attack = stats.attack.copy(reach=stats.attack.reach or 0 + 5)
        stats = stats.copy(attack=new_attack)
        return stats, [malleable_form(stats), feature]


class _Split(PowerBackport):
    def __init__(self):
        super().__init__(name="Split", power_type=PowerType.Creature, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ooze(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        feature = Feature(
            name="Split",
            action=ActionType.Reaction,
            description=f"Whenever {stats.selfref} takes lightning or slashing damage and it is Medium or larger, it splits in two if it has at least 10 hit points. Each new ooze has hit points equal to half the original ooze's, rounding down. New oozes are one size smaller than the original ooze.",
        )

        return stats, [malleable_form(stats), feature]


class _Transparent(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Transparent", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_ooze(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        feature = Feature(
            name="Transparent",
            action=ActionType.Feature,
            description=f"Even when {stats.selfref} is in plain sight, it takes a successful DC 15 Perception check to spot {stats.selfref} if it has neither moved nor attacked. \
                A creature that tries to enter {stats.selfref}'s space is surprised by {stats.selfref}",
        )

        return stats, [malleable_form(stats), feature]


class _LifeLeech(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Life Leech", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_ooze(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(0.5 * stats.attack.average_damage, suggested_die=Die.d6)

        feature = Feature(
            name="Life Leech",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"One Medium or smaller creature that {stats.selfref} can see within 5 feet of it must succeed on a DC {dc} Dexterity saving throw or be **Grappled** (escape DC {dc}). \
                Until this grapple ends, the target is **Restrained** and is unable to breathe. In addition, the target takes {dmg.description} ongoing necrotic damage at the start of each of its turns while grappled in this way. \
                While grappling the target, {stats.selfref} takes only half of any damage dealt to it (rounded down), and the target takes the other half.",
        )

        return stats, [malleable_form(stats), feature]


class _SlimeSpray(PowerBackport):
    def __init__(self):
        super().__init__(name="Slime Spray", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_ooze(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Slime Breath",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=6,
            description=f"{stats.selfref.capitalize()} sprays slimy goo in a 30-foot cone. Each creature in that area must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg.description} acid damage and is pulled up to 30 feet toward {stats.selfref}. On a success, the creature takes half as much damage and isn't pulled.",
        )

        return stats, [malleable_form(stats), feature]


ElongatedLimbs: Power = _ElongatedLimbs()
LifeLeech: Power = _LifeLeech()
OozingPassage: Power = _OozingPassage()
SlimeSpray: Power = _SlimeSpray()
Split: Power = _Split()
Transparent: Power = _Transparent()


OozePowers: List[Power] = [
    ElongatedLimbs,
    LifeLeech,
    OozingPassage,
    SlimeSpray,
    Split,
    Transparent,
]
