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


class _Incubation(Power):
    def __init__(self):
        super().__init__(name="Incubation", power_type=PowerType.Theme)
        self.damage_types = {DamageType.Necrotic, DamageType.Poison}

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.attack_type != AttackType.MeleeNatural:
            return NO_AFFINITY

        creature_types = {
            CreatureType.Aberration: HIGH_AFFINITY,
            CreatureType.Monstrosity: MODERATE_AFFINITY,
            CreatureType.Beast: LOW_AFFINITY,
        }
        score += creature_types.get(candidate.creature_type, 0)

        if candidate.secondary_damage_type in self.damage_types:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(attack_type=AttackType.MeleeNatural)

        if stats.secondary_damage_type not in self.damage_types:
            damage_type_indx = rng.choice(len(self.damage_types))
            damage_type = list(self.damage_types)[damage_type_indx]
            stats = stats.copy(secondary_damage_type=damage_type)

        dc = stats.difficulty_class_easy
        timespan = "three months" if stats.cr <= 5 else "three days"

        feature = Feature(
            name="Incubation",
            action=ActionType.Feature,
            description=f"If a humanoid is hit by {stats.selfref}'s attack, it must make a DC {dc} Constitution saving throw. \
                            On a failure, the target is infected by a terrible parasite. The target can carry only one such parasite at a time. \
                            Over the next {timespan}, the parasite gestates and moves to the chest cavity. \
                            In the 24-hour period before the parasite gives birth, the target feels unwell. Its speed is halved, and it has disadvantage on attack rolls, ability checks, and saving throws. \
                            At birth, the parasite burrows its way out of the target's chest in one round, killing it.\
                            If the disease is cured, the parasite disintigrates.",
        )

        return stats, feature


EraseMemory: Power = _EraseMemory()
WarpReality: Power = _WarpReality()
AdhesiveSkin: Power = _AdhesiveSkin()
Incubation: Power = _Incubation()

AberrantPowers: List[Power] = [EraseMemory, WarpReality, AdhesiveSkin]
