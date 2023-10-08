from math import ceil, floor
from typing import Dict, List, Tuple

from numpy.random import Generator

from ...attack_template import natural, spell
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Swallowed
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_aberration(
    candidate: BaseStatblock,
    min_size: Size | None = None,
    attack_modifiers: Dict[str, float] | None = None,
) -> float:
    if candidate.creature_type != CreatureType.Aberration:
        return NO_AFFINITY

    if min_size and candidate.size < min_size:
        return NO_AFFINITY

    score = HIGH_AFFINITY

    default_attack_modifier = attack_modifiers.get("*", 0) if attack_modifiers else 0
    attack_modifier = (
        attack_modifiers.get(candidate.attack.name, default_attack_modifier)
        if attack_modifiers
        else 0
    )

    score += attack_modifier
    return score if score > 0 else NO_AFFINITY


class _GraspingTentacles(Power):
    """Grasping Tentacles (Reaction). When this creature hits with an attack,
    they sprout a tentacle that grasps the target. In addition to the attack's normal effects, the target is grappled (escape
    DC = 11 + 1/2 CR) and restrained. Until the grapple ends, this creature can't use the grappling tentacle against another
    target. This creature can sprout 1d4 tentacles."""

    def __init__(self):
        super().__init__(name="Grasping Tentacles", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_aberration(
            candidate,
            attack_modifiers={natural.Tentacle.attack_name: HIGH_AFFINITY, "*": NO_AFFINITY},
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = int(floor(11 + 0.5 * stats.cr))
        feature = Feature(
            name="Grasping Tentacles",
            description=f"On a hit, the target sprouts a tentacle that grapples the target (escape DC {dc}). While grappled in this way, the target is restrained.",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )
        return stats, feature


class _DominatingGaze(Power):
    def __init__(self):
        super().__init__(name="Dominating Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_aberration(
            candidate, attack_modifiers={spell.Gaze.attack_name: HIGH_AFFINITY}
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Dominating Gaze",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=1,
            description=f"One target of this creature's choice that they can see within 60 feet must succed on a DC {dc} Charisma saving throw \
                or be forced to immediately use their reaction to move up to half their speed and make their most effective weapon attack or at-will spell or magical attack against a target chosen by this creature. \
                This counts as a **Charm** effect.",
        )
        return stats, feature


class _MaddeningWhispers(Power):
    def __init__(self):
        super().__init__(name="Maddening Whispers", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_aberration(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Madenning Whispers",
            action=ActionType.Feature,
            description=f"Each creature that starts its turn within 20 ft of {stats.selfref} must make a DC {dc} Wisdom saving throw. \
                On a failure, the creature can't take reactions until the start of its next turn and rolls a d8 to determine what it does during its turn. \
                On a 1-4, the creature does nothing. On a 5-6, the creature takes no action or bonus action and uses all its movement to move in a randomly determined direction. \
                On a 7-8, the creature makes a melee attack against a randomly determined creature within its reach or does nothing if it can't make such an attack.",
        )

        return stats, feature


class _TentacleSlam(Power):
    def __init__(self):
        super().__init__(name="Tentacle Slam", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_aberration(
            candidate,
            attack_modifiers={"*": NO_AFFINITY, natural.Tentacle.attack_name: HIGH_AFFINITY},
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(0.5 * stats.attack.average_damage, suggested_die=Die.d6)

        feature = Feature(
            name="Tentacle Slam",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} makes an attack against a creature within its reach. If the attack hits, the target is **Grappled** (escape DC {dc}). \
                Then, {stats.selfref} slams each creature grappled by it into each other or a solid surface. \
                Each creature must succeed on a DC {dc} Constitution saving throw or take {dmg.description} bludgeoning damage and be **Stunned** until the end of {stats.selfref}'s next turn.",
        )
        return stats, feature


class _AntimagicGullet(Power):
    def __init__(self):
        super().__init__(name="Anti-Magic Gullet", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_aberration(
            candidate,
            min_size=Size.Large,
            attack_modifiers={
                "*": -1 * MODERATE_AFFINITY,
                natural.Bite.attack_name: EXTRA_HIGH_AFFINITY,
            },
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        threshold = easy_multiple_of_five(2 * stats.cr, min_val=5, max_val=40)
        swallowed = Swallowed(
            damage=DieFormula.target_value(5 + stats.cr, force_die=Die.d4),
            regurgitate_dc=easy_multiple_of_five(threshold * 0.75, min_val=15, max_val=25),
            regurgitate_damage_threshold=threshold,
        )

        bite_attack = stats.attack.scale(
            scalar=1.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Swallow",
            additional_description=f"On a hit, the target must make a DC {dc} Dexterity saving throw. On a failure, it is {swallowed} Also see *Anti-Magic Gullet*.",
        )

        stats = stats.add_attack(bite_attack)

        feature = Feature(
            name="Anti-Magic Gullet",
            action=ActionType.Feature,
            description=f"Magical effects, including those produced by spells and magic items but excluding those created by artifacts or deities, are suppressed inside {stats.selfref}'s gullet. \
                Any spell slot or charge expended by a creature in the gullet to cast a spell or activate a property of a magic item is wasted. \
                No spell or magical effect that originates outside {stats.selfref}'s gullet, except one created by an artifact or a deity, can affect a creature or an object inside the gullet.",
        )

        return stats, feature


AntimagicGullet: Power = _AntimagicGullet()
DominatingGaze: Power = _DominatingGaze()
GraspingTentacles: Power = _GraspingTentacles()
MadenningWhispers: Power = _MaddeningWhispers()
TentacleSlam: Power = _TentacleSlam()

AberrationPowers: List[Power] = [
    AntimagicGullet,
    DominatingGaze,
    GraspingTentacles,
    MadenningWhispers,
    TentacleSlam,
]
