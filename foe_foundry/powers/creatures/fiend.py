from math import ceil, floor
from typing import Dict, List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, DamageType, Fatigue
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import AttackNames, score


def score_fiend(
    candidate: BaseStatblock,
    min_cr: float | None = None,
    attack_names: AttackNames = None,
) -> float:
    return score(
        candidate=candidate,
        require_types=CreatureType.Fiend,
        require_cr=min_cr,
        attack_names=attack_names,
    )


class _EmpoweredByDeath(PowerBackport):
    def __init__(self):
        super().__init__(name="Empowered by Death", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        hp = easy_multiple_of_five(2 * stats.cr, min_val=5, max_val=30)

        feature = Feature(
            name="Empowered by Death",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp} hp whenever a creature dies within 30 ft. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        return stats, feature


class _RelishYourFailure(PowerBackport):
    def __init__(self):
        super().__init__(name="Relish Your Failure", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        hp = DieFormula.target_value(max(2, stats.cr / 2), suggested_die=Die.d4)
        dc = stats.difficulty_class
        feature1 = Feature(
            name="Relish Your Failure",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} regains {hp.description} hp whenever a creature fails a saving throw within 60 feet. If it is at maximum hp, it gains that much temporary hp instead.",
        )

        feature2 = Feature(
            name="Fiendish Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} casts the *Bane* spell (spell save DC {dc}) at 2nd level, targeting up to 4 creatures, and without requiring concentration.",
        )

        return stats, [feature1, feature2]


class _FiendishTeleporation(PowerBackport):
    def __init__(self):
        super().__init__(name="Fiendish Teleportation", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        multiplier = 1.5 if stats.multiattack >= 2 else 0.75
        dmg = DieFormula.target_value(
            multiplier * stats.attack.average_damage, force_die=Die.d10
        )
        distance = easy_multiple_of_five(stats.cr * 10, min_val=30, max_val=120)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fiendish Teleportation",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} disappears and reappars in a burst of flame. It teleports up to {distance} feet to an unoccupied location it can see. \
                Each other creature within 10 feet of {stats.selfref} either before or after it teleports must make a DC {dc} Dexterity saving throw. On a failure, it takes {dmg.description} fire damage.",
        )
        return stats, feature


class _WallOfFire(PowerBackport):
    def __init__(self):
        super().__init__(name="Wall of Fire", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, min_cr=5)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy

        if stats.cr <= 7:
            uses = 1
            concentration = ""
        elif stats.cr <= 11:
            uses = 1
            concentration = " without requiring concentration"
        else:
            uses = 3
            concentration = " without requiring concentration"

        feature = Feature(
            name="Wall of Fire",
            action=ActionType.Action,
            replaces_multiattack=2,
            uses=uses,
            description=f"{stats.selfref.capitalize()} magically casts the *Wall of Fire* spell (spell save DC {dc}){concentration}.",
        )
        return stats, feature


class _FiendishBite(PowerBackport):
    def __init__(self):
        super().__init__(name="Fiendish Bite", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, attack_names=natural_attacks.Bite)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class

        def customize(a: Attack) -> Attack:
            return a.split_damage(DamageType.Poison, split_ratio=0.9)

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            name="Fiendish Bite",
            die=Die.d6,
            attack_type=AttackType.MeleeNatural,
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become **Poisoned** for 1 minute (save ends at end of turn).",
            callback=customize,
        )

        return stats, []


class _FiendishSummons(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Fiendish Summons", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, min_cr=3)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        _, _, description = summoning.determine_summon_formula(
            summoner=summoning.Fiends, summon_cr_target=stats.cr / 2.5, rng=rng
        )

        feature = Feature(
            name="Fiendish Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} summons forth additional fiendish allies. {description}",
        )

        return stats, feature


class _TemptingOffer(PowerBackport):
    def __init__(self):
        super().__init__(name="Tempting Offer", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate, min_cr=3)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        fatigue = Fatigue()
        feature = Feature(
            name="Tempting Offer",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} makes a tempting offer to a creature that can hear it within 60 feet. \
                That creature must make a DC {dc} Wisdom saving throw. On a failure, the creature gains a level of {fatigue}. \
                The creature may instead accept the offer. In doing so, it loses all levels of fatigue gained in this way but is contractually bound to the offer",
        )
        return stats, feature


class _DevilsSight(PowerBackport):
    def __init__(self):
        super().__init__(name="Devil's Sight", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_fiend(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        stats = stats.copy(creature_type=CreatureType.Fiend)

        level = 2 if stats.cr <= 5 else 4

        devils_sight = Feature(
            name="Devil's Sight",
            action=ActionType.Feature,
            description=f"Magical darkness doesn't impede {stats.selfref}'s darkvision, and it can see through Hellish Darkness.",
        )

        darkness = Feature(
            name="Hellish Darkness",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes shadowy black flames to fill a 15-foot radius sphere with obscuring darkness centered at a point within 60 feet that {stats.selfref} can see. \
                The darkness spreads around corners. Creatures without Devil's Sight can't see through this darkness and nonmagical light can't illuminate it. \
                If any of this spell's area overlaps with an area of light created by a spell of level {level} or lower, the spell that created the light is dispelled. \
                Creatures of {stats.selfref}'s choice lose any resistance to fire damage while in the darkness, and immunity to fire damage is instead treated as resistance to fire damage.",
        )

        return stats, [devils_sight, darkness]


DevilsSight: Power = _DevilsSight()
EmpoweredByDeath: Power = _EmpoweredByDeath()
FiendishBite: Power = _FiendishBite()
FiendishSummons: Power = _FiendishSummons()
FiendishTeleportation: Power = _FiendishTeleporation()
RelishYourFailure: Power = _RelishYourFailure()
TemptingOffer: Power = _TemptingOffer()
WallOfFire: Power = _WallOfFire()

FiendishPowers: List[Power] = [
    DevilsSight,
    EmpoweredByDeath,
    FiendishBite,
    FiendishSummons,
    FiendishTeleportation,
    RelishYourFailure,
    TemptingOffer,
    WallOfFire,
]
