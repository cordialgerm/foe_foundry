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
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _EraseMemory(Power):
    def __init__(self):
        super().__init__(name="Erase Memory", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        creature_types = {
            CreatureType.Aberration: HIGH_AFFINITY,
            CreatureType.Fey: HIGH_AFFINITY,
            CreatureType.Humanoid: LOW_AFFINITY,
        }

        roles = {
            MonsterRole.Controller: HIGH_AFFINITY,
            MonsterRole.Ambusher: MODERATE_AFFINITY,
            MonsterRole.Skirmisher: LOW_AFFINITY,
        }

        if candidate.creature_type not in creature_types:
            return NO_AFFINITY

        score = 0
        score += creature_types[candidate.creature_type]
        score += roles.get(candidate.role, 0)

        if candidate.attack_type.is_spell():
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_stats = stats.attributes.copy(primary_attribute=Stats.CHA)
        stats = stats.copy(
            attributes=new_stats,
            secondary_damage_type=DamageType.Psychic,
            attack_type=AttackType.RangedSpell,
        )

        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Erase Memory",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} becomes invisible to the target as the target's memories of {stats.selfref} are temporarily erased. \
                The target makes a DC {dc} Intelligence saving throw at the end of each of its turns to end the effect. \
                If a creature fails three saves, the memory loss is permanent and can only be undone with a Greater Restoration or equivalent magic. \
                A creature that succeeds on a saving throw is immune to this effect for 5 minutes.",
        )
        return stats, feature


class _WarpReality(Power):
    def __init__(self):
        super().__init__(name="Warp Reality", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.creature_type == CreatureType.Aberration:
            score += MODERATE_AFFINITY

        if candidate.attack_type.is_spell():
            score += MODERATE_AFFINITY

        if candidate.secondary_damage_type == DamageType.Psychic:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        distance = 20 + (20 if stats.cr >= 7 else 0)
        feature = Feature(
            name="Warp Reality",
            description=f"Each creature of {stats.selfref}'s choice within 30 ft must succeed on a DC {dc} Intelligence save or be teleported up to {distance} ft to an unoccupied space that {stats.selfref} can see.\
                If the target space is a hazard (such as an open pit, lava, or in the air) then the target may use its reaction to attempt a DC {dc} Dexterity save.\
                On a success, the target reduces the damage taken from the hazard this turn by half, or narrowly escapes the hazard. Creatures may choose to fail this save.",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=4,
        )
        return stats, feature


class _AdhesiveSkin(Power):
    def __init__(self):
        super().__init__(name="Adhesive Skin", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.creature_type in {CreatureType.Aberration, CreatureType.Ooze}:
            score += HIGH_AFFINITY

        if candidate.creature_type in {CreatureType.Monstrosity, CreatureType.Construct}:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Adhesive Skin",
            action=ActionType.Feature,
            description=f"When {stats.selfref} is hit by a melee weapon attack, the weapon becomes stuck to them. \
                A creature can use an action to remove the weapon with a successful DC 14 Athletics check. \
                All items stuck to {stats.selfref} become unstuck when it dies.",
        )

        return stats, feature


EraseMemory: Power = _EraseMemory()
WarpReality: Power = _WarpReality()
AdhesiveSkin: Power = _AdhesiveSkin()

AberrantPowers: List[Power] = [EraseMemory, WarpReality, AdhesiveSkin]
