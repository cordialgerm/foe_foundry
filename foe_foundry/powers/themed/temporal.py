from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import score


def score_temporal(candidate: BaseStatblock, min_cr: float | None = None) -> float:
    creature_types = {
        CreatureType.Fey,
        CreatureType.Fiend,
        CreatureType.Aberration,
        CreatureType.Humanoid,
    }

    def is_magical_human(c: BaseStatblock) -> bool:
        if c.creature_type == CreatureType.Humanoid:
            return c.attack_type.is_spell() and c.secondary_damage_type != DamageType.Radiant
        else:
            return c.creature_type in creature_types

    return score(
        candidate=candidate,
        require_types={
            CreatureType.Fey,
            CreatureType.Fiend,
            CreatureType.Aberration,
            CreatureType.Humanoid,
        },
        require_callback=is_magical_human,
        require_cr=min_cr,
        bonus_roles=MonsterRole.Controller,
    )


class _CurseOfTheAges(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Curse of the Ages", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate=candidate, min_cr=7)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(2.5 * stats.attack.average_damage, force_die=Die.d12)

        feature = Feature(
            name="Curse of the Ages",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=3,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 90 feet and curses it with rapid aging. \
                The target must make a DC {dc} Constitution saving throw, taking {dmg.description} necrotic damage on a failed save, or half as much on a success. \
                On a failure, the target also ages to the point where it has only 30 days left before it dies of old age. \
                Only a *wish* spell or *greater restoration* cast with a 9th-level spell slot can end this effect and restore the target to its previous age.",
        )

        return stats, feature


class _TemporalLoop(PowerBackport):
    def __init__(self):
        super().__init__(name="Temporal Loop", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=3)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        distance = 30
        uses = ceil(stats.cr / 7)

        feature1 = Feature(
            name="Temporal Record",
            action=ActionType.Feature,
            description=f"Whenever another creature within {distance} feet makes a d20 test, {stats.selfref} can record the d20 result (no action required). \
                If it already has a result recorded, then that result is overwritten with the new die roll.",
        )

        feature2 = Feature(
            name="Temporal Loop",
            action=ActionType.Reaction,
            uses=uses,
            description=f"Whenever a creature within {distance} feet makes a d20 test, {stats.selfref} can replace the result of the d20 roll \
                            with the die result it has recorded with its *Temporal Record* feature. The die result is then cleared.",
        )

        return stats, [feature1, feature2]


class _TemporalMastery(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Temporal Mastery", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=7)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        feature = Feature(
            name="Temporal Mastery",
            action=ActionType.Action,
            uses=2,
            replaces_multiattack=2,
            description=f"{stats.selfref} becomes **Invisible** until the start of its next turn. It may also adjust its initiative to any value it desires. \
                This can allow {stats.selfref} to have a second turn this round.",
        )

        return stats, feature


class _Accelerate(Power):
    def __init__(self):
        super().__init__(
            name="Accelerate Time", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=4)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Accelerate Time",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} touches a friendly creature. For the next 1 minute, that creature's movement speed is doubled \
                and it gains advantage on melee attacks.",
        )

        return [feature]


class _AlterFate(Power):
    def __init__(self):
        super().__init__(name="Alter Fate", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=4)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Alter Fate",
            action=ActionType.Reaction,
            recharge=5,
            description=f"When a creature that {stats.selfref} can see within 60 feet succeeds on an attack roll, ability check, or a saving throw, \
                then {stats.selfref} alters that creature's fate. It must reroll the d20 and use the lower roll.",
        )
        return [feature]


class _WallOfTime(Power):
    def __init__(self):
        super().__init__(name="Wall of Time", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=7)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Wall of Time",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a shimmering wall of temporal magic. The wall is either 60 feet long, 20 feet high, and 1 foot thick \
                or is a circular wall 20 feet in diameter, 20 feet high, and 1 foot thick. Nonmagical ranged attacks that cross the wall vanish into time with no other effect. \
                Ranged spell and magical attacks that pass through the wall are made with disadvantage. A creature that intentionally enters or passes through the wall is affected \
                as if they had just failed their initial saving throw against the *Slow* spell",
            replaces_multiattack=2,
        )
        return [feature]


class _Reset(Power):
    def __init__(self):
        super().__init__(name="Reset", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_temporal(candidate, min_cr=5)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature = Feature(
            name="Temporal Reset",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} twists time around up to four creatures of its choice. \
                If the creature is friendly, it may re-roll its initiative twice and keep the result that it prefers. \
                If the creature is hostile, it must make a DC {dc} Wisdom saving throw. On a failure, \
                the creature must re-roll its initiative twice and take the lower result.",
        )

        return [feature]


Accelerate: Power = _Accelerate()
AlterFate: Power = _AlterFate()
CurseOfTheAges: Power = _CurseOfTheAges()
TemporalLoop: Power = _TemporalLoop()
TemporalMastery: Power = _TemporalMastery()
TemporalReset: Power = _Reset()
WallOfTime: Power = _WallOfTime()

TemporalPowers: List[Power] = [
    Accelerate,
    AlterFate,
    CurseOfTheAges,
    TemporalLoop,
    TemporalMastery,
    TemporalReset,
    WallOfTime,
]
