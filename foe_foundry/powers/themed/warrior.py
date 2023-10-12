from typing import Dict, List, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Dazed
from ...die import Die
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
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
    candidate: BaseStatblock,
    requires_training: bool,
    large_size_boost: bool = False,
    requires_weapon: bool = False,
    attack_modifiers: AttackModifiers = None,
) -> float:
    if not candidate.attack_type.is_melee():
        return 0

    if requires_weapon and candidate.attack_type != AttackType.MeleeWeapon:
        return 0

    score = 0

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

    score += resolve_attack_modifier(candidate, attack_modifiers)

    return score


def _as_melee_fighter(stats: BaseStatblock, uses_weapon: bool = False) -> BaseStatblock:
    new_attrs = stats.attributes.copy(primary_attribute=Stats.STR)

    changes: dict = dict(attributes=new_attrs)
    if uses_weapon:
        changes.update(attack_type=AttackType.MeleeWeapon)
    return stats.copy(**changes)


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
            candidate,
            requires_training=False,
            large_size_boost=True,
            attack_modifiers={
                natural.Claw: HIGH_AFFINITY,
                weapon.Greataxe: HIGH_AFFINITY,
                weapon.Greatsword: MODERATE_AFFINITY,
                weapon.Maul: MODERATE_AFFINITY,
            },
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


class _PommelStrike(Power):
    def __init__(self):
        super().__init__(name="Pommel Strike", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_melee_fighter(
            candidate,
            requires_training=True,
            requires_weapon=True,
            attack_modifiers=[
                weapon.SwordAndShield,
                weapon.SpearAndShield,
            ],
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, None]:
        dazed = Dazed()
        dc = stats.difficulty_class_easy

        attack = stats.attack.scale(
            scalar=0.6,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeWeapon,
            reach=5,
            die=Die.d4,
            replaces_multiattack=1,
            name="Pommel Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        stats = stats.add_attack(attack)
        return stats, None


class _PushingAttack(Power):
    def __init__(self):
        super().__init__(name="Pushing Attack", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_melee_fighter(
            candidate,
            requires_training=False,
            requires_weapon=False,
            large_size_boost=True,
            attack_modifiers={
                "*": -1 * HIGH_AFFINITY,
                weapon.Maul: HIGH_AFFINITY,
                natural.Claw: HIGH_AFFINITY,
                natural.Slam: HIGH_AFFINITY,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        if stats.size >= Size.Huge:
            distance = 15
        elif stats.size >= Size.Large:
            distance = 10
        else:
            distance = 5

        feature = Feature(
            name="Pushing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is pushed up to {distance} feet horizontally.",
        )

        return stats, feature


Challenger: Power = _Challenger()
CleavingStrike: Power = _CleavingStrike()
Disciplined: Power = _Disciplined()
PackTactics: Power = _PackTactics()
ParryAndRiposte: Power = _ParryAndRiposte()
PommelStrike: Power = _PommelStrike()
PushingAttack: Power = _PushingAttack()
MageSlayer: Power = _MageSlayer()

WarriorPowers: List[Power] = [
    Challenger,
    CleavingStrike,
    Disciplined,
    PackTactics,
    ParryAndRiposte,
    PommelStrike,
    PushingAttack,
    MageSlayer,
]
