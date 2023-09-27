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
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _skirmisher_requirements(
    candidate: BaseStatblock,
    require_skirmisher: bool = True,
    dex_based: bool = True,
    requires_tactics: bool = False,
) -> float:
    score = 0

    # skirmishing units were typically made up of poor, lightly-armored soldiers
    candidate_could_use_tactics = (
        candidate.creature_type in {CreatureType.Humanoid} and candidate.cr <= 2
    )

    if require_skirmisher and candidate.role != MonsterRole.Skirmisher:
        return NO_AFFINITY

    if requires_tactics and not candidate_could_use_tactics:
        return NO_AFFINITY

    if candidate.role == MonsterRole.Ambusher:
        score += MODERATE_AFFINITY

    if dex_based and candidate.primary_attribute == Stats.DEX:
        score += MODERATE_AFFINITY

    if not dex_based and candidate.primary_attribute == Stats.STR:
        score += MODERATE_AFFINITY

    if candidate_could_use_tactics:
        score += MODERATE_AFFINITY

    return score if score > 0 else NO_AFFINITY


class _Nimble(Power):
    def __init__(self):
        super().__init__(name="Nimble", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(candidate, require_skirmisher=False)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.delta(10)
        stats = stats.copy(speed=new_speed)
        feature = Feature(
            name="Nimble",
            description=f"{stats.roleref} ignores difficult terrain",
            action=ActionType.Feature,
        )

        return stats, feature


class _CarefulSteps(Power):
    def __init__(self):
        super().__init__(name="Careful Steps", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(candidate, require_skirmisher=False)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Careful Steps",
            description=f"{stats.roleref}'s movement does not provoke opportunity attacks until the end of their turn",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _KnockBack(Power):
    def __init__(self):
        super().__init__(name="Knock Back", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(candidate, require_skirmisher=False, dex_based=False)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        description = f"On a hit, the target is pushed up to 5 feet away from {stats.selfref}."
        if stats.cr >= 4:
            dc = stats.difficulty_class
            description += (
                f" The target must also succeed on a DC {dc} Strength save or be knocked prone."
            )

        feature = Feature(
            name="Knock Back",
            description=description,
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
        )
        return stats, feature


class _Skirmish(Power):
    def __init__(self):
        super().__init__(name="Skirmish", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(
            candidate, require_skirmisher=True, requires_tactics=True
        )

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
                Each creature within the cube must succeed on a DC {dc} Strength save or be Grappled (escape DC {dc}) and Restrained while grappled in this way.",
        )

        return stats, feature


class _HarrassingRetreat(Power):
    def __init__(self):
        super().__init__(name="Harassing Retreat", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(
            candidate, require_skirmisher=True, requires_tactics=True
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


class _Speedy(Power):
    def __init__(self):
        super().__init__(name="Speedy", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _skirmisher_requirements(candidate, require_skirmisher=False)

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
KnockBack: Power = _KnockBack()
Nimble: Power = _Nimble()
Skirmish: Power = _Skirmish()
Speedy: Power = _Speedy()


SkirmisherPowers: List[Power] = [
    CarefulSteps,
    HarassingRetreat,
    KnockBack,
    Nimble,
    Skirmish,
    Speedy,
]
