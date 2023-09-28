from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...ac import ArmorClass
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
from .organized import _score_could_be_organized


def _score_could_be_melee_fighter(
    candidate: BaseStatblock, requires_training: bool, large_size_boost: bool = False
) -> float:
    if not candidate.attack_type.is_melee():
        return 0

    score = 0
    if candidate.creature_type.could_use_weapon:
        score += MODERATE_AFFINITY

    if not requires_training and candidate.creature_type in {
        CreatureType.Beast,
        CreatureType.Monstrosity,
    }:
        score += MODERATE_AFFINITY

    if candidate.primary_attribute_score == Stats.STR:
        score += MODERATE_AFFINITY

    if candidate.role in {MonsterRole.Bruiser, MonsterRole.Default}:
        score += MODERATE_AFFINITY

    if large_size_boost and candidate.size >= Size.Large:
        score += MODERATE_AFFINITY

    return score


def _as_melee_fighter(stats: BaseStatblock, uses_weapon: bool = False) -> BaseStatblock:
    new_attrs = stats.attributes.copy(primary_attribute=Stats.STR)

    changes: dict = dict(attributes=new_attrs)
    if uses_weapon:
        changes.update(attack_type=AttackType.MeleeWeapon)
    return stats.copy(**changes)


class _PinningShot(Power):
    def __init__(self):
        super().__init__(name="Pinning Shot", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0

        if not candidate.attack_type.is_ranged():
            return NO_AFFINITY

        score = LOW_AFFINITY

        if candidate.role in {MonsterRole.Controller, MonsterRole.Artillery}:
            score += MODERATE_AFFINITY

        if candidate.primary_attribute == Stats.STR:
            score += LOW_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class

        name = "Pinning Shot" if stats.attack_type.is_ranged() else "Pinning Hit"

        feature = Feature(
            name=name,
            action=ActionType.Feature,
            description=f"On a hit, the target must succeed on a DC {dc} Strength saving throw or be **Restrained** (save ends at end of turn).",
            hidden=True,
            modifies_attack=True,
        )

        return stats, feature


class _Challenger(Power):
    def __init__(self):
        super().__init__(name="Challenger", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        if not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = 0

        if candidate.role == MonsterRole.Defender or candidate.creature_type.could_wear_armor:
            score += HIGH_AFFINITY

        if candidate.attributes.CHA >= 18 or candidate.attributes.has_proficiency_or_expertise(
            Skills.Intimidation
        ):
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Challenge Foe",
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} challenges the target to a duel. \
                The challenged target has disadvantage on attack rolls against any creature other than {stats.selfref}. \
                The target may make a DC {dc} Charisma saving throw at the end of each of its turns to end the effect.",
            action=ActionType.BonusAction,
            recharge=4,
        )
        return stats, feature


class _PackTactics(Power):
    def __init__(self):
        super().__init__(name="Pack Tactics", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_could_be_organized(candidate, requires_intelligence=False)
        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Pack Tactics",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack rolls against a target if at least one of {stats.selfref}'s allies is within 5 feet and isn't incapacitated.",
        )
        return stats, feature


class _CleavingStrike(Power):
    def __init__(self):
        super().__init__(name="Cleaving Strike", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_could_be_melee_fighter(
            candidate, requires_training=False, large_size_boost=True
        )
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_melee_fighter(stats)

        if stats.primary_damage_type == DamageType.Bludgeoning:
            name = "Sweeping Blow"
        elif stats.primary_damage_type == DamageType.Piercing:
            name = "Piercing Strike"
        elif stats.primary_damage_type == DamageType.Slashing:
            name = "Cleaving Strike"
        else:
            name = "Cleaving Strike"

        dc = stats.difficulty_class
        feature = Feature(
            name=name,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()}'s attack can hit a nearby target. Immediately after hitting with an attack, {stats.selfref} may choose another target within reach.\
                The target must make a DC {dc} Dexterity saving throw. On a failure, it takes half the damage of the original attack.",
        )
        return stats, feature


class _Disciplined(Power):
    def __init__(self):
        super().__init__(name="Disciplined", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = (
            _score_could_be_organized(candidate, requires_intelligence=True)
            + _score_could_be_melee_fighter(candidate, requires_training=True)
        ) / 2.0
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Disciplined",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} misses an attack or fails a saving throw while another friendly creature is within 10 feet, it may use its reaction to re-roll the attack or saving throw.",
        )
        return stats, feature


class _MageSlayer(Power):
    def __init__(self):
        super().__init__(name="Mage Slayer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        score = _score_could_be_melee_fighter(candidate, requires_training=True)
        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_melee_fighter(stats, uses_weapon=True)
        feature = Feature(
            name="Mage Slayer",
            action=ActionType.Reaction,
            description=f"If a hostile creature begins casting a spell within reach of {stats.selfref} then it may make a melee attack against the caster. \
                If the attack hits, the caster must make a Concentration check against the damage of the attack. On a failure, the spell fails.",
        )
        return stats, feature


class _ParryAndRiposte(Power):
    """This creature adds +3 to their Armor Class against one melee attack that would hit them.
    If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.
    """

    def __init__(self):
        super().__init__(name="Parry and Riposte", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        # this monster requires a melee weapon
        # it makes a ton of sense for defenders and leaders
        # clever and dextrous foes get a boost as well
        if candidate.attack_type != AttackType.MeleeWeapon:
            return NO_AFFINITY

        score = 0
        if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
            score += HIGH_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.WIS >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.DEX >= 14:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description=f"{stats.selfref.capitalize()} adds +3 to their Armor Class against one melee attack that would hit them.\
                         If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.",
            action=ActionType.Reaction,
            recharge=6,
        )
        return stats, feature


Challenger: Power = _Challenger()
CleavingStrike: Power = _CleavingStrike()
Disciplined: Power = _Disciplined()
PinningShot: Power = _PinningShot()
PackTactics: Power = _PackTactics()
ParryAndRiposte: Power = _ParryAndRiposte()
MageSlayer: Power = _MageSlayer()

WarriorPowers: List[Power] = [
    PinningShot,
    Challenger,
    PackTactics,
    ParryAndRiposte,
    CleavingStrike,
    Disciplined,
    MageSlayer,
]
