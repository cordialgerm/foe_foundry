from math import ceil, floor
from typing import Dict, List, Set, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural, spell
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType, Dazed, Swallowed
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..scoring import AttackNames, score


def _score_could_be_monstrous(
    candidate: BaseStatblock,
    min_size: Size | None = None,
    additional_creature_types: Set[CreatureType] | None = None,
    require_living: bool = True,
    attack_names: AttackNames = None,
) -> float:
    def is_living(c: BaseStatblock) -> bool:
        return c.creature_type.is_living

    creature_types = {CreatureType.Monstrosity, CreatureType.Beast}
    if additional_creature_types is not None:
        creature_types |= additional_creature_types

    return score(
        candidate=candidate,
        require_types=creature_types,
        require_callback=is_living if require_living else None,
        attack_names=attack_names,
        require_size=min_size,
    )


def _as_monstrous(candidate: BaseStatblock, boost_speed: int = 10) -> BaseStatblock:
    changes: dict = dict(attack_type=AttackType.MeleeNatural)

    if boost_speed != 0:
        new_speed = candidate.speed.delta(boost_speed)
        changes.update(speed=new_speed)

    return candidate.copy(**changes)


class _Constriction(PowerBackport):
    def __init__(self):
        super().__init__(name="Constriction", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(
            candidate, attack_names=["-", natural.Slam, natural.Tail]
        )

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


class _Swallow(PowerBackport):
    def __init__(self):
        super().__init__(name="Swallow", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(
            candidate,
            min_size=Size.Large,
            additional_creature_types={CreatureType.Ooze},
            attack_names={
                "-",
                natural.Bite,
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

        stats = stats.add_attack(
            scalar=1.7,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Swallow",
            additional_description=f"On a hit, the target must make a DC {dc} Dexterity saving throw. On a failure, it is {swallowed}",
        )

        return stats, None


class _Pounce(PowerBackport):
    def __init__(self):
        super().__init__(name="Pounce", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(candidate)

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


class _Corrosive(PowerBackport):
    def __init__(self):
        super().__init__(name="Corrosive", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(
            candidate,
            attack_names={
                "-",
                natural.Spit,
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


class _DevourAlly(PowerBackport):
    def __init__(self):
        super().__init__(name="Devour Ally", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)
        size = stats.size.decrement()
        hp = int(ceil(max(5 + stats.cr, 3 + 2 * stats.cr, 3 * stats.cr)))
        feature = Feature(
            name="Devour Ally",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} swallows an allied creature that is within 5 feet of this creature and is {size.capitalize()} or smaller. \
                {stats.selfref.capitalize()} regains {hp} hp and the devoured ally is reduced to 0 hp.",
        )
        return stats, feature


class _LingeringWound(PowerBackport):
    def __init__(self):
        super().__init__(name="Lingering Wound", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(
            candidate, attack_names=[natural.Bite, natural.Claw, natural.Horns]
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)

        dc = max(10, min(15, stats.difficulty_class_easy))
        dmg = DieFormula.target_value(0.75 * stats.attack.average_damage, force_die=Die.d6)
        bleeding = Bleeding(damage=dmg, dc=dc)
        feature = Feature(
            name="Lingering Wound",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"Immediately after hitting a creature, {stats.selfref} inflicts that creature with a lingering wound. \
                The creature gains {bleeding}",
        )
        return stats, feature


class _Rampage(PowerBackport):
    def __init__(self):
        super().__init__(name="Rampage", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_monstrous(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_monstrous(stats)

        feature = Feature(
            name="Rampage",
            action=ActionType.Reaction,
            description=f"When a creature within 30 feet is reduced to 0 hitpoints, {stats.selfref} may move up to half its speed and make an attack.",
        )

        return stats, feature


# TODO - A5E Basilisk
class _PetrifyingGaze(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Petrifying Gaze", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types={
                CreatureType.Monstrosity,
                CreatureType.Celestial,
                CreatureType.Undead,
            },
            bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
            attack_names={"-", spell.Gaze},
        )

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


# TODO A5E SRD - Bulette
# Jaw Clamp (1/Day). When an attacker
# within 5 feet of the bulette misses it with a
# melee attack, the bulette makes a bite
# attack against the attacker. On a hit, the
# attacker is grappled (escape DC 15). Until
# this grapple ends, the grappled creature
# is restrained, and the only attack the
# bulette can make is a bite against the
# grappled creature.


# TODO A5E SRD - Cockatrice
# Frenzy (1/Day). When attacked by a
# creature it can see within 20 feet, the
# cockatrice moves up to half its Speed and
# makes a bite attack against that creature.

# TODO A5E SRD - Glabrezu
# Rend. If grappling the same target with
# both pincers, the glabrezu rips at the
# target, ending both grapples and dealing
# 27 (4d10 + 5) slashing damage. If this
# damage reduces a creature to 0 hit
# points, it dies and is torn in half.


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
