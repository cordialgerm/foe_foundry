from math import ceil, floor
from typing import List, Set, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_is_sneaky_creature(
    candidate: BaseStatblock, additional_creature_types: Set[CreatureType] | None = None
) -> float:
    score = 0

    if candidate.role == MonsterRole.Ambusher:
        score += HIGH_AFFINITY

    if candidate.role == MonsterRole.Skirmisher:
        score += MODERATE_AFFINITY

    if candidate.primary_attribute == Stats.DEX:
        score += LOW_AFFINITY

    if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
        score += MODERATE_AFFINITY

    if (
        additional_creature_types is not None
        and candidate.creature_type in additional_creature_types
    ):
        score += HIGH_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _CunningAction(PowerBackport):
    def __init__(self):
        super().__init__(name="Cunning Action", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Cunning Action",
            description="Dash, Disengage, or Hide",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _SneakyStrike(PowerBackport):
    def __init__(self):
        super().__init__(name="Sneaky Strike", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = DieFormula.target_value(max(1.5 * stats.cr, 2 + stats.cr), force_die=Die.d6)

        feature = Feature(
            name="Sneaky Strike",
            description=f"{stats.roleref.capitalize()} deals an additional {dmg.description} damage immediately after hitting a target if the attack was made with advantage.",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _FalseAppearance(PowerBackport):
    def __init__(self):
        super().__init__(
            name="False Appearance", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(
            candidate,
            additional_creature_types={
                CreatureType.Plant,
                CreatureType.Construct,
                CreatureType.Ooze,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="False Appearance",
            action=ActionType.Feature,
            description=f"As long as {stats.selfref} remains motionless it is indistinguishable from its surrounding terrain.",
        )

        return stats, feature


class _NotDeadYet(PowerBackport):
    """When this creature is reduced to 0 hit points, they drop prone and are indistinguishable from a dead creature.
    At the start of their next turn, this creature stands up without using any movement and has 2x CR hit points.
    They can then take their turn normally."""

    def __init__(self):
        super().__init__(name="Not Dead Yet", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for undead, oozes, beasts, and monstrosities
        score = LOW_AFFINITY
        if candidate.creature_type in {
            CreatureType.Ooze,
            CreatureType.Undead,
            CreatureType.Beast,
            CreatureType.Monstrosity,
        }:
            score += HIGH_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += MODERATE_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        hp = easy_multiple_of_five(int(ceil(2.0 * stats.cr)))

        feature = Feature(
            name="Not Dead Yet",
            description=f"When {stats.selfref} is reduced to 0 hit points, it drops prone and is indistinguishable from a dead creature. \
                        At the start of their next turn, {stats.selfref} stands up without using any movement and has {hp} hit points. It can take its turn normally",
            action=ActionType.Reaction,
            uses=1,
        )
        return stats, feature


class _Vanish(PowerBackport):
    """This creature can use the Disengage action, then can hide if they have cover"""

    def __init__(self):
        super().__init__(name="Vanish", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Vanish",
            description=f"{stats.selfref.capitalize()} can use the Disengage action, then can hide if they have cover.",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _StayDown(PowerBackport):
    def __init__(self):
        super().__init__(name="Stay Down", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        reach = stats.attack.reach or 5

        feature = Feature(
            name="Stay Down",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} kicks a prone creature within {reach} ft. The target must make a DC {dc} Strength \
                save or have its speed reduced to zero until the end of its next turn.",
        )

        return stats, feature


class _ExploitAdvantage(PowerBackport):
    def __init__(self):
        super().__init__(name="Exploit Advantage", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_is_sneaky_creature(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Exploit Advantage",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.selfref.capitalize()} gains advantage on the next attack it makes until end of turn.",
        )

        return stats, feature


CunningAction: Power = _CunningAction()
ExploitAdvantage: Power = _ExploitAdvantage()
FalseAppearance: Power = _FalseAppearance()
SneakyStrike: Power = _SneakyStrike()
StayDown: Power = _StayDown()
NotDeadYet: Power = _NotDeadYet()
Vanish: Power = _Vanish()


SneakyPowers: List[Power] = [
    CunningAction,
    ExploitAdvantage,
    FalseAppearance,
    SneakyStrike,
    StayDown,
    NotDeadYet,
    Vanish,
]
