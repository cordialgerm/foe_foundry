from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import choose_enum, easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_clever(candidate: BaseStatblock) -> float:
    # This power makes sense for any non-beast monster with reasonable mental stats
    if (
        candidate.creature_type == CreatureType.Beast
        or candidate.role == MonsterRole.Bruiser
        or candidate.attributes.INT <= 10
        or candidate.attributes.WIS <= 10
        or candidate.attributes.CHA <= 10
    ):
        return NO_AFFINITY

    score = LOW_AFFINITY

    if candidate.attributes.INT >= 16:
        score += LOW_AFFINITY

    if candidate.attributes.CHA >= 16:
        score += LOW_AFFINITY

    if candidate.attributes.WIS >= 16:
        score += LOW_AFFINITY

    if candidate.role in {MonsterRole.Leader, MonsterRole.Controller}:
        score += MODERATE_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _Keen(Power):
    """This creature has a keen mind"""

    def __init__(self):
        super().__init__(name="Keen", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_clever(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        # give the monster reasonable mental stats

        n = min(int(ceil(stats.cr / 5)), 3)

        skills = choose_enum(
            rng,
            [
                Skills.Persuasion,
                Skills.Deception,
                Skills.Insight,
                Skills.Intimidation,
                Skills.Perception,
            ],
            size=n,
        ) + [Skills.Investigation]
        saves = choose_enum(rng, [Stats.WIS, Stats.INT, Stats.CHA], size=n)

        new_attrs = (
            stats.attributes.boost(Stats.CHA, 2)
            .boost(Stats.INT, 2)
            .boost(Stats.WIS, 2)
            .grant_proficiency_or_expertise(*skills)
            .grant_save_proficiency(*saves)
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Identify Weakness",
            action=ActionType.Reaction,
            description=f"When an ally that {stats.selfref} can see misses an attack against a hostile target, {stats.selfref} can make an Investigation check with a DC equal to the hostile target's AC. \
                On a success, the attack hits instead of missing.",
        )
        return stats, feature


class _MarkTheTarget(Power):
    """When this creature hits a target with a ranged attack, allies of this creature who can see the target
    have advantage on attack rolls against the target until the start of this creature's next turn.
    """

    def __init__(self):
        super().__init__(name="Mark the Target", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for leaders, artillery, controllers, high intelligence foes, and ranged foes
        score = LOW_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attack_type in {AttackType.RangedSpell, AttackType.RangedWeapon}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Leader}:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mark the Target",
            description=f"Immediately after hitting a target, {stats.selfref} can mark the target. All allies of {stats.selfref} who can see the target have advantage on attack rolls against the target until the start of this creature's next turn.",
            uses=3,
            action=ActionType.BonusAction,
        )
        return stats, feature


class _UnsettlingWords(Power):
    def __init__(self):
        super().__init__(name="Unsettling Words", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_clever(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        uses = ceil(stats.cr / 7)
        distance = easy_multiple_of_five(5 + 1.25 * stats.cr, min_val=10, max_val=30)

        if stats.cr <= 5:
            die = DieFormula.from_expression("1d4")
        elif stats.cr <= 11:
            die = DieFormula.from_expression("1d6")
        else:
            die = DieFormula.from_expression("1d8")

        feature = Feature(
            name="Unsettling Words",
            action=ActionType.Reaction,
            uses=uses,
            description=f"Whenever a hostile creature within {distance} that can hear {stats.selfref} makes a d20 ability check, \
                {stats.selfref} can roll {die} and subtract the result from the total, potentially turning a success into a failure",
        )

        return stats, feature


Keen: Power = _Keen()
MarkTheTarget: Power = _MarkTheTarget()
UnsettlingWords: Power = _UnsettlingWords()


CleverPowers: List[Power] = [Keen, MarkTheTarget, UnsettlingWords]
