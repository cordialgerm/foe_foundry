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
from ..scoring import score


def score_sneaky(
    candidate: BaseStatblock, additional_creature_types: Set[CreatureType] | None = None, **args
) -> float:
    return score(
        candidate=candidate,
        require_roles=[MonsterRole.Ambusher, MonsterRole.Skirmisher, MonsterRole.Leader],
        require_stats=Stats.DEX,
        bonus_skills=Skills.Stealth,
        bonus_types=additional_creature_types,
        stat_threshold=16,
        **args,
    )


class _CunningAction(PowerBackport):
    def __init__(self):
        super().__init__(name="Cunning Action", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_sneaky(candidate)

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
        return score_sneaky(candidate, require_attack_types=AttackType.AllWeapon())

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
        return score_sneaky(
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


class _Vanish(PowerBackport):
    """This creature can use the Disengage action, then can hide if they have cover"""

    def __init__(self):
        super().__init__(name="Vanish", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_sneaky(candidate)

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
        return score_sneaky(candidate, require_attack_types=AttackType.AllMelee())

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
        return score_sneaky(candidate)

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
Vanish: Power = _Vanish()


SneakyPowers: List[Power] = [
    CunningAction,
    ExploitAdvantage,
    FalseAppearance,
    SneakyStrike,
    StayDown,
    Vanish,
]
