from math import ceil, floor
from typing import Dict, List, Tuple

import numpy as np
from numpy.random import Generator

from ...attack_template import natural
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Dazed, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import LOW_POWER, Power, PowerBackport, PowerType
from ..scoring import AttackNames, score


def score_giant(
    candidate: BaseStatblock,
    attack_names: AttackNames = None,
    min_cr: float | None = None,
) -> float:
    return score(
        candidate=candidate,
        require_types=CreatureType.Giant,
        require_cr=min_cr,
        attack_names=attack_names,
        bonus_size=Size.Huge,
    )


class _ForcefulBlow(PowerBackport):
    def __init__(self):
        super().__init__(name="Forceful Blow", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        if stats.size >= Size.Gargantuan:
            die = "d8"
        elif stats.size >= Size.Huge:
            die = "d6"
        else:
            die = "d4"

        feature = Feature(
            name="Forceful Blow",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting a target with a weapon attack, {stats.selfref} forcefully pushes the target back. \
                Roll {die}+1. The target is pushed away from {stats.selfref} by 5 times that many feet.",
        )

        return stats, feature


class _ShoveAllies(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Forceful Blow", power_type=PowerType.Creature, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate, attack_names=natural.Slam)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shove Allies",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} can shove any allied creatures who are within 5 feet and are smaller in size. \
                Each shoved ally moves up to 15 feet away from {stats.selfref} and can make a melee weapon attack if they end that movement and have a viable target within their reach.",
        )

        return stats, feature


class _Boulder(PowerBackport):
    def __init__(self):
        super().__init__(name="Boulder", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        dc = stats.difficulty_class_easy
        if stats.multiattack >= 3:
            dmg = int(floor(1.5 * stats.attack.average_damage))
        else:
            dmg = int(ceil(1.25 * stats.attack.average_damage))

        dmg = DieFormula.target_value(dmg, suggested_die=stats.size.hit_die())

        if stats.cr >= 12:
            distance = 60
            radius = 20
        elif stats.cr >= 8:
            distance = 45
            radius = 15
        elif stats.cr >= 4:
            distance = 30
            radius = 10
        else:
            distance = 20
            radius = 5

        feature = Feature(
            name="Boulder",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} tosses a boulder at a point it can see within {distance} ft. Each creature within a {radius} ft radius must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg.description} bludgeoning damage and is knocked prone. On a success, the creature takes half damage and is not knocked prone.",
        )

        return stats, feature


class _CloudRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Cloud Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Lightning}, upgrade_resistance_to_immunity_if_present=True
        )

        new_attributes = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(
            secondary_damage_type=DamageType.Lightning, attributes=new_attributes
        )

        feature = Feature(
            name="Cloud Rune",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} or a creature it can see is hit by an attack roll, {stats.selfref} can invoke a Cloud Rune \
                and choose a different creature within 30 feet of {stats.selfref}. The chosen creature becomes the target of the attack. \
                This magic can transfer the attack's effect regardless of the attack's range.",
        )

        return stats, feature


class _FireRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Fire Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Fire}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Fire)
        dmg = DieFormula.target_value(
            target=0.33 * stats.attack.average_damage, suggested_die=Die.d6
        )
        burning = conditions.Burning(dmg)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Fire Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} invokes the fire run. \
                The target takes an extra {dmg.description} fire damage and must make a DC {dc} Strength save. On a failure, the creature is **Restrained** (save ends at end of turn). \
                While restrained in this way, the creature is {burning.caption}. {burning.description_3rd}",
        )

        return stats, feature


class _FrostRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Frost Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Cold}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Cold)

        dc = stats.difficulty_class_easy
        dmg = int(ceil(0.5 * stats.attack.average_damage))
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Frost Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} invokes the frost run. \
                The target takes an extra {dmg} cold damage and must make a DC {dc} Constitution save or become {frozen.caption}. \
                {frozen.description_3rd}",
        )

        return stats, feature


class _StoneRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Stone Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Stone Rune",
            action=ActionType.Reaction,
            uses=1,
            description=f"When a creature ends its turn within 30 feet of {stats.selfref}, {stats.selfref} can activate the stone rune. \
                The creature must make a DC {dc} Wisdom save. On a failure, the creature is **Charmed** for 1 minute (save ends at end of turn). \
                While charmed in this way, the creature is **Incapacitated** in a dreamy stupor.",
        )

        return stats, feature


class _HillRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Hill Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Poison}, upgrade_resistance_to_immunity_if_present=True
        )

        feature = Feature(
            name="Stone Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} invokes the hill rune and gains resistance to bludgeoning, piercing, and slashing damage for 1 minute",
        )

        return stats, feature


class _StormRune(PowerBackport):
    def __init__(self):
        super().__init__(name="Storm Rune", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Lightning}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Lightning)

        feature = Feature(
            name="Storm Rune",
            action=ActionType.Reaction,
            uses=3,
            description=f"Whenever {stats.selfref} or another creature makes an attack roll, saving throw, or ability check, {stats.selfref} can force the roll to have advantage or disadvantage.",
        )

        return stats, feature


class _Earthshaker(PowerBackport):
    def __init__(self):
        super().__init__(name="Earthshaker", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_giant(candidate, attack_names=natural.Slam)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        dc = stats.difficulty_class_easy
        size = stats.size.decrement().decrement() if stats.size >= Size.Huge else Size.Medium
        distance1 = easy_multiple_of_five(1.5 * stats.cr, min_val=10, max_val=30)

        sizes = {Size.Gargantuan: 60, Size.Huge: 45, Size.Large: 30}
        distance2 = sizes.get(stats.size, 15)

        dazed = Dazed()

        feature1 = Feature(
            name="Earthshaker",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} moves, all {size} or smaller creatures that are within {distance1} feet of {stats.selfref} \
                must make a DC {dc} Strength check or fall **Prone**. A creature that falls prone in this way loses concentration.",
        )

        dmg = DieFormula.target_value(stats.attack.average_damage * 1.5, force_die=Die.d8)

        feature2 = Feature(
            name="Earthshaker Stomp",
            action=ActionType.Action,
            replaces_multiattack=2,
            uses=1,
            description=f"{stats.selfref.capitalize()} stomps its foot, creathing a massive shockwave. Each creature in a {distance2} ft cone \
                must make a DC {dc} Strength saving throw or take {dmg.description} Thunder damage and be {dazed}",
        )

        return stats, [feature1, feature2]


Boulder: Power = _Boulder()
CloudRune: Power = _CloudRune()
Earthshaker: Power = _Earthshaker()
FireRune: Power = _FireRune()
FrostRune: Power = _FrostRune()
HillRune: Power = _HillRune()
ForcefulBlow: Power = _ForcefulBlow()
StoneRune: Power = _StoneRune()
StormRune: Power = _StormRune()
ShoveAllies: Power = _ShoveAllies()


GiantPowers: List[Power] = [
    Boulder,
    CloudRune,
    Earthshaker,
    FireRune,
    FrostRune,
    ForcefulBlow,
    HillRune,
    StoneRune,
    StormRune,
    ShoveAllies,
]
