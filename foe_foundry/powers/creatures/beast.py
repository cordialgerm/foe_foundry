from math import ceil
from typing import Dict, List, Set, Tuple

from numpy.random import Generator

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import summoning
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def _score_beast(
    candidate: BaseStatblock,
    primary_attribute: Stats | None = None,
    attack_modifiers: AttackModifiers = None,
) -> float:
    return score(
        candidate=candidate,
        require_types=CreatureType.Beast,
        bonus_stats=primary_attribute,
        attack_modifiers=attack_modifiers,
    )


class _HitAndRun(PowerBackport):
    def __init__(self):
        super().__init__(name="Hit and Run", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.DEX)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Hit and Run",
            action=ActionType.BonusAction,
            description="This creature moves up to 30 feet without provoking opportunity attacks. \
                If it ends its movement behind cover or in an obscured area, it can make a Stealth check to hide.",
        )

        return stats, feature


class _MotivatedByCarnage(PowerBackport):
    def __init__(self):
        super().__init__(name="Motivated by Carnage", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.STR)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Survival)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Motivated by Carnage",
            action=ActionType.Reaction,
            description="When this creature reduces another target to below half its hit points or to 0 hit points, \
                         this creature can immediately move up to its speed and make a melee attack against another target. \
                         This Reaction can only activate once per target.",
        )

        return stats, feature


class _Gore(PowerBackport):
    def __init__(self):
        super().__init__(name="Gore", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate, Stats.STR, attack_modifiers=["-", natural_attacks.Horns])

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        dc = stats.difficulty_class

        bleeding_damage = DieFormula.target_value(0.75 * stats.attack.average_damage)
        bleeding = Bleeding(damage=bleeding_damage)

        gore_attack = stats.attack.scale(
            scalar=1.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            name="Gore",
            replaces_multiattack=2,
            additional_description=f"If {stats.selfref} moved at least 10 feet before making this attack, then the target must make a DC {dc} Dexterity saving throw. On a failure, the target is gored and gains {bleeding}.",
        )

        stats = stats.add_attack(gore_attack)

        return stats, None


class _Web(PowerBackport):
    def __init__(self):
        super().__init__(name="Web", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        attacks = {
            "-",
            natural_attacks.Bite,
            natural_attacks.Claw,
            natural_attacks.Stinger,
        }
        return _score_beast(candidate, Stats.STR, attacks)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        stats = stats.copy(speed=new_speed)

        dc = stats.difficulty_class

        feature1 = Feature(
            name="Spider Climb",
            action=ActionType.Feature,
            description=f"{stats.selfref} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check.",
        )

        feature2 = Feature(
            name="Web Sense",
            action=ActionType.Feature,
            description=f"While in contact with a web, {stats.selfref} knows the exact location of any other creature in contact with the same web.",
        )

        feature3 = Feature(
            name="Web",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} shoots a sticky web at a point it can see within 60 feet. \
                Each creature within a 20 foot cube centered at the point must make a DC {dc} Dexterity saving throw or become **Restrained** (save ends at end of turn). \
                The area of the web is considered difficult terrain, and any creature that ends its turn in the area must repeat the save or become restrained.",
        )

        return stats, [feature1, feature2, feature3]


class _Packlord(PowerBackport):
    def __init__(self):
        super().__init__(name="Packlord", power_type=PowerType.Creature, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        desired_summon_cr = ceil(stats.cr / 3.5)

        if stats.speed.fly:
            options = summoning.FlyingBeasts
        elif stats.speed.swim:
            options = summoning.SwimmingBeasts
        else:
            options = summoning.LandBeasts

        _, _, description = summoning.determine_summon_formula(
            options, desired_summon_cr, rng, max_quantity=10
        )

        feature = Feature(
            name="Packlord",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} roars, summoning its pack to its aid. {description}",
        )

        return stats, feature


class _WildInstinct(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Wild Instinct", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_beast(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Wild Instinct",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize} identifies the creature with the lowest Strength score that it can see. It then Dashes towards that creature.",
        )
        return stats, feature


Gore: Power = _Gore()
HitAndRun: Power = _HitAndRun()
MotivatedByCarnage: Power = _MotivatedByCarnage()
Packlord: Power = _Packlord()
Web: Power = _Web()
WildInstinct: Power = _WildInstinct()

BeastPowers: List[Power] = [Gore, HitAndRun, MotivatedByCarnage, Packlord, Web, WildInstinct]
