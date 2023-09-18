from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DelightsInSuffering(Power):
    """When attacking a target whose current hit points are below half their hit point maximum,
    this creature has advantage on attack rolls and deals an extra CR damage when they hit."""

    def __init__(self):
        super().__init__(name="Delights in Suffering", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for cruel enemies
        # cruel factors: Fiend, Monstrosity, Intimidation proficiency, Intimidation expertise, high charisma, Ambusher, Bruiser, Leader
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Fiend, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.expertise_skills:
            score += EXTRA_HIGH_AFFINITY
        if candidate.attributes.CHA >= 15:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser, MonsterRole.Leader}:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # grant intimidation proficiency or expertise
        stats = stats.copy(
            attributes=stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        )

        # use secondary damage type, if there is one
        # if there isn't, set it to poison
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        damage_type = stats.secondary_damage_type
        dmg = int(ceil(0.75 * stats.cr))
        feature = Feature(
            name="Delights in Suffering",
            description=f"The attack is made at advantage and deals an additional {dmg} {damage_type} damage if the target is at or below half-health.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return stats, feature


class _Lethal(Power):
    """This creature has a +CR bonus to damage rolls, and scores a critical hit on an unmodified attack roll of 18-20."""

    def __init__(self):
        super().__init__(name="Lethal", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this role makes sense for lots of monsters, but Ambushers and Artillery should be a bit more likely to have this
        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Artillery}:
            score += MODERATE_AFFINITY
        if candidate.secondary_damage_type == DamageType.Poison:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
        dmg = int(ceil(stats.cr))
        dmg_type = stats.secondary_damage_type

        crit_lower = 19 if stats.cr <= 7 else 18

        feature1 = Feature(
            name="Lethal",
            description=f"The attack scores a critical hit on an unmodified attack roll of {crit_lower}-20",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )

        feature2 = Feature(
            name="Lethal",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} deals an additional {dmg} {dmg_type} damage to the target",
        )
        return stats, [feature1, feature2]


DelightsInSuffering: Power = _DelightsInSuffering()
Lethal: Power = _Lethal()

CruelPowers: List[Power] = [
    DelightsInSuffering,
    Lethal,
]
