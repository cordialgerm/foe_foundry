from math import ceil
from typing import Dict, List, Tuple

import numpy as np

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_bruiser(
    candidate: BaseStatblock,
    size_boost: bool = False,
    attack_modifiers: Dict[str, float] | None = None,
) -> float:
    score = 0

    if candidate.role == MonsterRole.Bruiser:
        score += MODERATE_AFFINITY

    if size_boost and candidate.size >= Size.Large:
        score += MODERATE_AFFINITY

    default_attack_modifier = attack_modifiers.get("*", 0) if attack_modifiers else 0
    attack_modifier = (
        attack_modifiers.get(candidate.attack.name, default_attack_modifier)
        if attack_modifiers
        else default_attack_modifier
    )

    score += attack_modifier

    return score


# TODO - boost for Polearm
class _Sentinel(Power):
    def __init__(self):
        super().__init__(name="Sentinel", power_type=PowerType.Role)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_bruiser(candidate, size_boost=True)

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
        return _score_bruiser(
            candidate,
            attack_modifiers={
                natural_attacks.Slam.attack_name: EXTRA_HIGH_AFFINITY,
                "*": NO_AFFINITY,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Athletics)
        stats = stats.copy(attributes=new_attrs, primary_damage_type=DamageType.Bludgeoning)

        dc = stats.difficulty_class

        grapple_attack = stats.attack.scale(
            scalar=0.7,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Grappling Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save or be **Grappled** (escape DC {dc}). \
                 While grappled in this way, the creature is also **Restrained**",
        )

        stats = stats.add_attack(grapple_attack)

        return stats, None


# TODO - boost for Claw, Axe
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
            description=f"Immediately after the {stats.selfref} hits with a weapon attack, it may make the same attack against another target within its reach.",
            recharge=4,
        )

        return stats, feature


# TODO - boost for Club, Slam
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
            description=f"Immediately after the {stats.roleref} hits with a weapon attack, it may force the target to succeed on a DC {dc} Constitution save or be **Stunned** until the end of the {stats.selfref}'s next turn.",
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
            score += MODERATE_AFFINITY

        if candidate.attack_type == AttackType.MeleeNatural:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class

        rend_attack = stats.attack.scale(
            scalar=0.7,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeWeapon
            if stats.attack.attack_type != AttackType.MeleeNatural
            else AttackType.MeleeNatural,
            name="Rend",
        )
        dmg = DieFormula.target_value(rend_attack.average_rolled_damage, force_die=Die.d6)
        bleeding = Bleeding(damage=dmg)

        rend_attack = rend_attack.copy(
            additional_description=f"On a hit, the target must succeed on a DC {dc} Constitution saving throw or gain {bleeding}",
        )

        stats = stats.add_attack(rend_attack)

        return stats, []


Sentinel: Power = _Sentinel()
Grappler: Power = _Grappler()
Cleaver: Power = _Cleaver()
Basher: Power = _Basher()
Disembowler: Power = _Disembowler()

BruiserPowers: List[Power] = [Sentinel, Grappler, Cleaver, Basher, Disembowler]
