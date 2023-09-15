from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DistractingAttack(Power):
    def __init__(self):
        super().__init__(name="Distracting Attack", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Deception):
            score += MODERATE_AFFINITY

        if score == 0:
            return NO_AFFINITY
        else:
            return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Distracting Attack",
            action=ActionType.Feature,
            description=f"On a hit, {stats.roleref} can choose to become invisible until the start of their next turn.",
            hidden=True,
            modifies_attack=True,
        )

        return stats, feature


class _ShadowyMovement(Power):
    def __init__(self):
        super().__init__(name="Shadowy Movement", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Shadowy Movement",
            description=f"{stats.roleref.capitalize()} can attempt to hide in dim light or lightly obscured terrain. \
            When {stats.roleref} moves, they can make a Dexterity (Stealth) check to hide as part of that movement",
            action=ActionType.Feature,
        )

        return stats, feature


class _CunningAction(Power):
    def __init__(self):
        super().__init__(name="Elusive", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY

        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Cunning Action",
            description="Dash, Disengage, or Hide",
            action=ActionType.BonusAction,
        )

        return stats, feature


class _DeadlyAmbusher(Power):
    def __init__(self):
        super().__init__(name="Deadly Ambusher", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Ambusher:
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
            score += MODERATE_AFFINITY

        if candidate.speed.fastest_speed >= 40:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Deadly Ambusher",
            description=f"{stats.selfref.capitalize()} has advantage on initiative rolls. \
                On the first turn of combat, it has advantage on any attack rolls against targets with lower initiative than it, \
                and it scores a critical hit on a score of 19 or 20.",
            action=ActionType.Feature,
        )

        return stats, feature


class _SneakyStrike(Power):
    def __init__(self):
        super().__init__(name="Sneaky Strike", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Ambusher:
            score += MODERATE_AFFINITY

        if candidate.attack_type.is_ranged():
            score += MODERATE_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        if stats.cr <= 1:
            dmg = 2
        elif stats.cr <= 3:
            dmg = 2 * stats.cr
        elif stats.cr == 4:
            dmg = 6
        else:
            dmg = stats.cr + 1

        feature = Feature(
            name="Sneaky Strike",
            description=f"{stats.roleref.capitalize()} deals an additional {dmg} immediately after hitting a target if the attack was made with advantage.",
            action=ActionType.BonusAction,
        )

        return stats, feature


DistractingAttack: Power = _DistractingAttack()
ShadowyMovement: Power = _ShadowyMovement()
CunningAction: Power = _CunningAction()
DeadlyAmbusher: Power = _DeadlyAmbusher()
SneakyStrike: Power = _SneakyStrike()

AmbusherPowers: List[Power] = [
    DistractingAttack,
    ShadowyMovement,
    CunningAction,
    DeadlyAmbusher,
    SneakyStrike,
]
