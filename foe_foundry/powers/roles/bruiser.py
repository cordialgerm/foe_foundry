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
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Sentinel(Power):
    def __init__(self):
        super().__init__(name="Sentinel", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if candidate.role == MonsterRole.Bruiser:
            score += MODERATE_AFFINITY

        if candidate.size >= Size.Large:
            score += MODERATE_AFFINITY

        if candidate.attack_type == AttackType.MeleeWeapon:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Sentinel",
            action=ActionType.Reaction,
            description=f"If another target moves while within {stats.roleref}'s reach then the {stats.roleref} may make an attack against that target.",
        )

        return stats, feature


class _Grappler(Power):
    def __init__(self):
        super().__init__(name="Grappler", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = LOW_AFFINITY

        if candidate.role == MonsterRole.Bruiser:
            score += LOW_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += LOW_AFFINITY

        if candidate.attack_type == AttackType.MeleeNatural:
            score += LOW_AFFINITY

        if candidate.attributes.has_proficiency_or_expertise(Skills.Athletics):
            score += MODERATE_AFFINITY

        if candidate.primary_damage_type == DamageType.Bludgeoning:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs, primary_damage_type=DamageType.Bludgeoning)

        dc = stats.difficulty_class

        feature = Feature(
            name="Grappling Strike",
            action=ActionType.BonusAction,
            description=f"Immediately after {stats.roleref} hits with a weapon attack, the target must make a DC {dc} Strength save (escape DC {dc}). \
                 While grappled in this way, the creature is also restrained",
        )

        return stats, feature


class _Cleaver(Power):
    def __init__(self):
        super().__init__(name="Cleaver", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = LOW_AFFINITY

        if candidate.role == MonsterRole.Bruiser:
            score += LOW_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += LOW_AFFINITY

        if candidate.size >= Size.Large:
            score += MODERATE_AFFINITY

        if candidate.primary_damage_type == DamageType.Slashing:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(primary_damage_type=DamageType.Slashing)

        feature = Feature(
            name="Cleaving Blows",
            action=ActionType.BonusAction,
            description=f"Immediately after the {stats.selfref} hits with a weapon attack, it may make the same attack against a target within its reach.",
            recharge=5,
        )

        return stats, feature


class _Basher(Power):
    def __init__(self):
        super().__init__(name="Basher", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = LOW_AFFINITY

        if candidate.role == MonsterRole.Bruiser:
            score += LOW_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += LOW_AFFINITY

        if candidate.primary_damage_type == DamageType.Bludgeoning:
            score += MODERATE_AFFINITY

        if candidate.size >= Size.Large:
            score += MODERATE_AFFINITY

        if candidate.attributes.STR >= 15:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(primary_damage_type=DamageType.Bludgeoning)

        dc = stats.difficulty_class

        feature = Feature(
            name="Stunning Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after the {stats.roleref} hits with a weapon attack, it may force the target to succeed on a DC {dc} Constitution save or be Stunned until the end of the {stats.selfref}'s next turn.",
            recharge=6,
        )

        return stats, feature


class _Disembowler(Power):
    def __init__(self):
        super().__init__(name="Disembowler", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = 0

        if candidate.role == MonsterRole.Bruiser:
            score += MODERATE_AFFINITY

        if candidate.primary_damage_type == DamageType.Piercing:
            score += LOW_AFFINITY

        if candidate.attack_type == AttackType.MeleeNatural:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        dmg = ceil(stats.cr)

        feature = Feature(
            name="Rend",
            action=ActionType.BonusAction,
            description=f"Immediately after {stats.roleref} hits with a weapon attack, it may force the target to succeed on a DC {dc} Constitution saving throw or suffer {dmg} ongoing piercing damage at the start of each of its turns. \
                The ongoing damage ends when the creature receives magical healing, or if the creature or another creature uses an action to perform a DC 10 Medicine check",
        )

        return stats, feature


Sentinel: Power = _Sentinel()
Grappler: Power = _Grappler()
Cleaver: Power = _Cleaver()
Basher: Power = _Basher()
Disembowler: Power = _Disembowler()

BruiserPowers: List[Power] = [Sentinel, Grappler, Cleaver, Basher, Disembowler]
