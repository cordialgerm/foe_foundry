from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
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


def score_cruel(
    candidate: BaseStatblock, require_melee: bool = False, min_cr: float | None = None
) -> float:
    # this power makes a lot of sense for cruel enemies
    # cruel factors: Fiend, Monstrosity, Intimidation proficiency, Intimidation expertise, high charisma, Ambusher, Bruiser, Leader
    if require_melee and not candidate.attack_type.is_melee():
        return NO_AFFINITY

    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    score = 0
    if candidate.creature_type in {CreatureType.Fiend, CreatureType.Monstrosity}:
        score += HIGH_AFFINITY
    if candidate.attributes.has_proficiency_or_expertise(Skills.Intimidation):
        score += HIGH_AFFINITY
    if candidate.attributes.CHA >= 15:
        score += MODERATE_AFFINITY
    if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser, MonsterRole.Leader}:
        score += MODERATE_AFFINITY
    return score if score > 0 else NO_AFFINITY


class _DelightsInSuffering(Power):
    """When attacking a target whose current hit points are below half their hit point maximum,
    this creature has advantage on attack rolls and deals an extra CR damage when they hit."""

    def __init__(self):
        super().__init__(name="Delights in Suffering", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_cruel(candidate, min_cr=3)

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
        dmg = DieFormula.target_value(1 + 0.5 * stats.cr, suggested_die=Die.d6)
        feature = Feature(
            name="Delights in Suffering",
            description=f"The attack is made at advantage and deals an additional {dmg.description} {damage_type} damage if the target is at or below half-health.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return stats, feature


class _Lethal(Power):
    def __init__(self):
        super().__init__(name="Lethal", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_cruel(candidate, require_melee=True, min_cr=7)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        crit_lower = 19 if stats.cr <= 7 else 18
        dmg = DieFormula.target_value(2 + stats.cr, force_die=Die.d6)
        dmg_type = stats.secondary_damage_type or stats.primary_damage_type
        feature = Feature(
            name="Lethal",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} scores a critical hit on an unmodified attack roll of {crit_lower}-20. \
                Additional, a critical hit from {stats.selfref} deals an additional {dmg.description} {dmg_type} damage (do not apply crit modifier to this damage), and the creature dies if this attack reduces its hit points to 0.",
        )

        return stats, feature


DelightsInSuffering: Power = _DelightsInSuffering()
Lethal: Power = _Lethal()

CruelPowers: List[Power] = [
    DelightsInSuffering,
    Lethal,
]
