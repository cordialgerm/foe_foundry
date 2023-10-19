from math import ceil
from typing import List, Tuple

import numpy as np
from num2words import num2words
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def _score_physically_tough(candidate: BaseStatblock) -> float:
    # this role makes sense for lots of monsters, but Defenders and Bruisers should be a bit more likely to have this
    return score(
        candidate=candidate,
        require_types=[
            CreatureType.Ooze,
            CreatureType.Undead,
            CreatureType.Beast,
            CreatureType.Monstrosity,
        ],
        bonus_roles=[MonsterRole.Bruiser, MonsterRole.Defender],
        bonus_stats=Stats.STR,
        require_stats=Stats.CON,
        stat_threshold=14,
        bonus_skills=[Skills.Deception, Skills.Performance],
    )


def _score_has_magic_protection(candidate: BaseStatblock) -> float:
    # this is common amongst fiends, celestials, and fey and high-CR creatures
    return score(
        candidate=candidate,
        require_types=[CreatureType.Fey, CreatureType.Fiend, CreatureType.Celestial],
        bonus_roles=[MonsterRole.Defender, MonsterRole.Leader],
        require_cr=5,
    )


class _NotDeadYet(PowerBackport):
    """When this creature is reduced to 0 hit points, they drop prone and are indistinguishable from a dead creature.
    At the start of their next turn, this creature stands up without using any movement and has 2x CR hit points.
    They can then take their turn normally."""

    def __init__(self):
        super().__init__(name="Not Dead Yet", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for undead, oozes, beasts, and monstrosities
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Ooze,
                CreatureType.Undead,
                CreatureType.Beast,
                CreatureType.Monstrosity,
            ],
            require_stats=Stats.CON,
            stat_threshold=14,
            bonus_skills=[Skills.Deception, Skills.Performance],
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        hp = int(ceil(2.0 * stats.cr))

        feature = Feature(
            name="Not Dead Yet",
            description=f"When {stats.selfref} is reduced to 0 hit points, it drops prone and is indistinguishable from a dead creature. \
                        At the start of their next turn, {stats.selfref} stands up without using any movement and has {hp} hit points. It can take its turn normally",
            action=ActionType.Reaction,
            uses=1,
        )
        return stats, feature


class _GoesDownFighting(PowerBackport):
    """When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious."""

    def __init__(self):
        super().__init__(
            name="Goes Down Fighting", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_physically_tough(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _AdrenalineRush(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Adrenaline Rush", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_physically_tough(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Adrenaline Rush",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )

        return stats, feature


class _MagicResistance(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Magic Resistance", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_has_magic_protection(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Magic Resistance",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on saves against spells and other magical effects.",
        )

        return stats, feature


class _LimitedMagicImmunity(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Limited Magic Immunity", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_has_magic_protection(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        level = (
            f"{num2words(int(min(5, ceil(stats.cr / 3))), to='ordinal')} level spell or lower"
        )

        feature = Feature(
            name="Limited Magic Immunity",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is attacked by a spell, targeted by spell, or forced to make a saving throw by a {level} then {stats.selfref} can force the spell attack to miss or can choose to succeed on the saving throw.",
        )

        return stats, feature


class _QuickRecovery(PowerBackport):
    """Quick Recovery (Trait). At the start of this creature's turn, they can attempt a saving throw
    against any effect on them that can be ended by a successful saving throw."""

    def __init__(self):
        super().__init__(
            name="Quick Recovery", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for high CR creatures, creatures with high CON (resilient), or high CHA (luck)
        return _score_physically_tough(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        # add CON save proficiency
        new_attrs = stats.attributes.grant_save_proficiency(Stats.CON)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Quick Recovery",
            description=f"At the start of {stats.selfref}'s turn, they can attempt a saving throw \
                         against any effect on them that can be ended by a successful saving throw",
            action=ActionType.Feature,
        )
        return stats, feature


class _Regeneration(PowerBackport):
    def __init__(self):
        super().__init__(name="Regeneration", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_physically_tough(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        weaknesses = {
            CreatureType.Undead: "radiant damage",
            CreatureType.Monstrosity: "acid or fire damage",
            CreatureType.Construct: "acid damage",
            CreatureType.Elemental: "necrotic damage",
        }
        weakness = weaknesses.get(stats.creature_type, "fire damage")
        hp = easy_multiple_of_five(1.5 * stats.cr)

        feature = Feature(
            name="Regeneration",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp at the start of its turn. \
                If {stats.selfref} takes {weakness}, this trait doesn't function at the start of {stats.selfref}'s next turn. \
                {stats.selfref.capitalize()} only dies if it starts its turn with 0 hp and doesn't regenerate.",
        )
        return stats, feature


class _Stoneskin(PowerBackport):
    def __init__(self):
        super().__init__(name="Stoneskin", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_physically_tough(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Stoneskin",
            action=ActionType.Reaction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} instantly hardens its exterior in response to being hit by an attack. \
                {stats.selfref.capitalize()} gains resistance to non-psychic damage until the end of its next turn",
        )

        return stats, feature


AdrenalineRush: Power = _AdrenalineRush()
GoesDownFighting: Power = _GoesDownFighting()
LimitedMagicImmunity: Power = _LimitedMagicImmunity()
MagicResistance: Power = _MagicResistance()
NotDeadYet: Power = _NotDeadYet()
QuickRecovery: Power = _QuickRecovery()
Regeneration: Power = _Regeneration()
Stoneskin: Power = _Stoneskin()

ToughPowers: List[Power] = [
    AdrenalineRush,
    GoesDownFighting,
    LimitedMagicImmunity,
    MagicResistance,
    NotDeadYet,
    QuickRecovery,
    Regeneration,
    Stoneskin,
]
