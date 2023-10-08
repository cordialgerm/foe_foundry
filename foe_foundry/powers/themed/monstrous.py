from math import ceil, floor
from typing import Dict, List, Set, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural as natural_attacks
from ...attack_template import spell as spell_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Dazed, Swallowed
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


def _score_could_be_monstrous(
    candidate: BaseStatblock,
    min_size: Size | None = None,
    additional_creature_types: Dict[CreatureType, float] | None = None,
    require_living: bool = True,
    attack_adjustments: Dict[str, float] | None = None,
) -> float:
    if require_living and not candidate.creature_type.is_living:
        return 0

    if min_size is not None and candidate.size < min_size:
        return NO_AFFINITY

    score = 0
    creature_types = {
        CreatureType.Monstrosity: HIGH_AFFINITY,
        CreatureType.Beast: HIGH_AFFINITY,
    }

    if additional_creature_types is not None:
        creature_types.update(additional_creature_types)

    score += creature_types.get(candidate.creature_type, 0)

    default_attack_adjustment = attack_adjustments.get("*", 0) if attack_adjustments else 0
    attack_adjustment = (
        attack_adjustments.get(candidate.attack.name, default_attack_adjustment)
        if attack_adjustments
        else 0
    )

    score += attack_adjustment

    return score


def _as_monstrous(candidate: BaseStatblock, boost_speed: int = 10) -> BaseStatblock:
    changes: dict = dict(attack_type=AttackType.MeleeNatural)

    if boost_speed != 0:
        new_speed = candidate.speed.delta(boost_speed)
        changes.update(speed=new_speed)

    return candidate.copy(**changes)


def _score(candidate: BaseStatblock, **args) -> float:
    score = _score_could_be_monstrous(candidate, **args)
    return score if score > 0 else NO_AFFINITY


class _Constriction(Power):
    def __init__(self):
        super().__init__(name="Constriction", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        reach = 5 if stats.size <= Size.Medium else 10
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(max(2, ceil(stats.cr)), force_die=Die.d4)

        feature = Feature(
            name="Constrict",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} chooses a target it can see within {reach} feet. The target must make a DC {dc} Strength saving throw or become **Grappled** (escape DC {dc}). \
                While grappled in this way, the target is also **Restrained** and takes {dmg.description} ongoing bludgeoning damage at the start of each of its turns.",
        )
        return stats, feature


class _Swallow(Power):
    def __init__(self):
        super().__init__(name="Swallow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(
            candidate,
            min_size=Size.Large,
            additional_creature_types={CreatureType.Ooze: HIGH_AFFINITY},
            attack_adjustments={
                "*": -1 * MODERATE_AFFINITY,
                natural_attacks.Bite.attack_name: EXTRA_HIGH_AFFINITY,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        stats = _as_monstrous(stats)

        dc = stats.difficulty_class
        threshold = easy_multiple_of_five(3 * stats.cr, min_val=5, max_val=40)
        swallowed = Swallowed(
            damage=DieFormula.target_value(6 + stats.cr, force_die=Die.d4),
            regurgitate_dc=easy_multiple_of_five(threshold * 0.85, min_val=15, max_val=25),
            regurgitate_damage_threshold=threshold,
        )

        swallow_attack = stats.attack.scale(
            scalar=1.7,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Swallow",
            additional_description=f"On a hit, the target must make a DC {dc} Dexterity saving throw. On a failure, it is {swallowed}",
        )

        stats = stats.add_attack(swallow_attack)

        return stats, None


class _Pounce(Power):
    def __init__(self):
        super().__init__(name="Pounce", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        dc = stats.difficulty_class
        feature = Feature(
            name="Pounce",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} jumps 20 feet toward a creature it can see, attempting to knock it prone. The target must make a DC {dc} Strength save or be knocked prone. \
                Then, {stats.selfref} makes an attack against the target.",
        )

        return stats, feature


class _Corrosive(Power):
    def __init__(self):
        super().__init__(name="Corrosive", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(
            candidate,
            attack_adjustments={
                "*": -1 * HIGH_AFFINITY,
                natural_attacks.Spit.attack_name: EXTRA_HIGH_AFFINITY,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats, boost_speed=0)
        stats = stats.copy(secondary_damage_type=DamageType.Acid)
        dc = stats.difficulty_class
        dmg = int(ceil(max(5, 2 * stats.cr)))
        feature = Feature(
            name="Corrode",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets a creature within 30 feet that it can see and spits a glob of corrosive acid. \
                The target must make a DC {dc} Dexterity save. On a failure, the target takes {dmg} acid damage, and one non-magical metallic item the target carries begins to corrode. \
                If the object is a weapon, it takes a permanent and cumulative -1 penalty to damage rolls. If its penalty drops to -5, the weapon is destroyed. \
                If the object is either metal armor or a shield it takes a permanent and cumulative -1 penalty to the AC it offers. \
                Armor reduced to an AC of 10 or a shield that drops to a +0 bonus is destroyed.",
        )
        return stats, feature


class _DevourAlly(Power):
    def __init__(self):
        super().__init__(name="Devour Ally", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        size = stats.size.decrement()
        hp = int(ceil(max(5 + stats.cr, 3 + 2 * stats.cr, 3 * stats.cr)))
        feature = Feature(
            name="Devour Ally",
            action=ActionType.BonusAction,
            description=f"{stats.selfref} swallows an allied creature that is within 5 feet of this creature and is {size.capitalize()} or smaller. \
                {stats.selfref.capitalize()} regains {hp} hp and the devoured ally is reduced to 0 hp.",
        )
        return stats, feature


class _LingeringWound(Power):
    def __init__(self):
        super().__init__(name="Lingering Wound", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        if stats.primary_damage_type.is_physical:
            stats = stats.copy(primary_damage_type=DamageType.Piercing)

        dc = max(10, min(15, stats.difficulty_class_easy))
        dmg = int(floor(0.75 * stats.attack.average_damage))
        dmg_type = stats.attack.damage.damage_type
        feature = Feature(
            name="Lingering Wound",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"Immediately after hitting a creature, {stats.selfref} inflicts that creature with a lingering wound. \
                The wounded creature takes {dmg} ongoing {dmg_type} damage at the end of each of its turns. \
                The target may attempt a DC {dc} Constitution save at the end of each of its turns to end the effect. \
                A creature may also use an action to perform a DC {dc} Medicine check to end the lingering wound.",
        )
        return stats, feature


class _Rampage(Power):
    def __init__(self):
        super().__init__(name="Rampage", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)

        feature = Feature(
            name="Rampage",
            action=ActionType.Reaction,
            description=f"When a creature within 30 feet is reduced to 0 hitpoints, {stats.selfref} may move up to half its speed and make an attack.",
        )

        return stats, feature


class _PetrifyingGaze(Power):
    def __init__(self):
        super().__init__(name="Petrifying Gaze", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        creature_types = {
            CreatureType.Monstrosity: MODERATE_AFFINITY,
            CreatureType.Celestial: LOW_AFFINITY,
            CreatureType.Undead: LOW_AFFINITY,
        }

        score = creature_types.get(candidate.creature_type, 0)

        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Controller}:
            score += MODERATE_AFFINITY

        if candidate.attack.name == spell_attacks.Gaze.attack_name:
            score += HIGH_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        dazed = Dazed()

        feature = Feature(
            name="Petrifying Gaze",
            action=ActionType.Reaction,
            recharge=4,
            description=f"Whenever a creature within 60 feet looks at {stats.selfref}, it must make a DC {dc} Constitution saving throw. \
                On a failed save, the creature magically begins to turn to stone and is {dazed}. It must repeat the saving throw at the end of its next turn. \
                On a success, the effect ends. On a failure, the creature is **Petrified** until it is freed by the *Greater Restoration* spell or other magic.",
        )

        return stats, feature


Constriction: Power = _Constriction()
Corrosive: Power = _Corrosive()
DevourAlly: Power = _DevourAlly()
LingeringWound: Power = _LingeringWound()
PetrifyingGaze: Power = _PetrifyingGaze()
Pounce: Power = _Pounce()
Rampage: Power = _Rampage()
Swallow: Power = _Swallow()


MonstrousPowers: List[Power] = [
    Constriction,
    Corrosive,
    DevourAlly,
    LingeringWound,
    PetrifyingGaze,
    Pounce,
    Rampage,
    Swallow,
]
