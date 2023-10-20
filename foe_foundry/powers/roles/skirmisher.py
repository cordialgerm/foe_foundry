from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock, MonsterDials
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..scoring import score


def score_skirmisher(candidate: BaseStatblock, requires_tactics: bool = True, **args) -> float:
    def ideal_skirmisher(c: BaseStatblock) -> bool:
        # skirmishing units were typically made up of poor, lightly-armored soldiers
        return c.creature_type in {CreatureType.Humanoid} and c.cr <= 2

    def is_organized(c: BaseStatblock) -> bool:
        return c.creature_type.could_be_organized

    return score(
        candidate=candidate,
        require_roles=MonsterRole.Skirmisher,
        bonus_roles=MonsterRole.Skirmisher,
        bonus_stats=Stats.DEX,
        bonus_speed=40,
        bonus_callback=ideal_skirmisher,
        require_callback=is_organized if requires_tactics else None,
        **args,
    )


class _Nimble(PowerBackport):
    def __init__(self):
        super().__init__(name="Nimble", power_type=PowerType.Role, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_skirmisher(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.delta(10)
        stats = stats.copy(speed=new_speed)
        feature = Feature(
            name="Nimble",
            description=f"{stats.roleref.capitalize()} ignores difficult terrain",
            action=ActionType.Feature,
        )

        return stats, feature


class _CarefulSteps(PowerBackport):
    def __init__(self):
        super().__init__(name="Careful Steps", power_type=PowerType.Role, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_skirmisher(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Careful Steps",
            description=f"{stats.roleref.capitalize()}'s movement does not provoke opportunity attacks until the end of their turn",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _Skirmish(PowerBackport):
    def __init__(self):
        super().__init__(name="Skirmish", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_skirmisher(candidate, requires_tactics=True)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        net_size = 10 if stats.cr <= 4 else 15
        net_range = 60 if stats.size >= Size.Large else 30

        feature = Feature(
            name="Skirmisher Nets",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
            description=f"{stats.roleref.capitalize()} throws a net in a {net_size} ft. cube at a point it can see within {net_range} ft. \
                Each creature within the cube must succeed on a DC {dc} Strength save or be **Grappled** (escape DC {dc}) and **Restrained** while grappled in this way.",
        )

        return stats, feature


class _HarrassingRetreat(PowerBackport):
    def __init__(self):
        super().__init__(name="Harassing Retreat", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return score_skirmisher(
            candidate, requires_tactics=True, require_attack_types=AttackType.AllRanged()
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(attack_type=AttackType.RangedWeapon)

        feature = Feature(
            name="Harassing Retreat",
            action=ActionType.Reaction,
            recharge=5,
            description=f"When a hostile creature ends movement within 10 feet of {stats.roleref}, it may move up to half its movement. \
                 As part of this reaction, it makes a ranged attack against the triggering creature.",
        )

        return stats, feature


class _Speedy(PowerBackport):
    def __init__(self):
        super().__init__(name="Speedy", power_type=PowerType.Role, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_skirmisher(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        # give the monster reasonable DEX stat
        new_attrs = (
            stats.attributes.boost(Stats.DEX, 2)
            .grant_proficiency_or_expertise(Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX)
        )
        stats = stats.copy(attributes=new_attrs).apply_monster_dials(
            MonsterDials(speed_modifier=10)
        )

        feature = Feature(
            name="Speedy",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement increases by 10ft and it gains proficiency in Acrobatics and Dexterity saves",
        )
        return stats, feature


CarefulSteps: Power = _CarefulSteps()
HarassingRetreat: Power = _HarrassingRetreat()
Nimble: Power = _Nimble()
Skirmish: Power = _Skirmish()
Speedy: Power = _Speedy()


SkirmisherPowers: List[Power] = [
    CarefulSteps,
    HarassingRetreat,
    Nimble,
    Skirmish,
    Speedy,
]
