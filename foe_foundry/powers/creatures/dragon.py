from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)
from ..themed.breath import BreathAttack


def _score_dragon(candidate: BaseStatblock, high_cr_boost: bool = False) -> float:
    if candidate.creature_type != CreatureType.Dragon:
        return NO_AFFINITY

    score = HIGH_AFFINITY

    if high_cr_boost:
        score += MODERATE_AFFINITY

    return score


class _DragonsGaze(Power):
    def __init__(self):
        super().__init__(name="Dragon's Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        dc = stats.difficulty_class
        dmg = int(max(3, stats.cr / 2))

        feature = Feature(
            name="Dragon's Gaze",
            action=ActionType.BonusAction,
            recharge=6,
            description=f"One creature within 60 feet of {stats.selfref} that can see it must make a DC {dc} Wisdom save or be **Frightened** of {stats.selfref} (save ends at end of turn). \
                While frightened in this way, each time the target takes damage, they take an additional {dmg} psychic damage.",
        )

        return stats, feature


class _DraconicRetaliation(Power):
    def __init__(self):
        super().__init__(name="Draconic Retaliation", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate, high_cr_boost=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        hp = easy_multiple_of_five(stats.hp.average / 2)
        uses = 1
        description = f"When {stats.selfref} is reduced to {hp} hit points or fewer, it may immediately use either its breath weapon or Multiattack action. \
            If {stats.selfref} is incapacitated or otherwise unable to use this trait, it may use it the next time they are able."

        if stats.cr >= 15:
            uses = 2
            hp2 = int(ceil(hp / 2))
            description += f" {stats.selfref.capitalize()} may activate this ability again when reduced to {hp2} hit points or fewer."

        feature = Feature(
            name="Draconic Retaliation",
            action=ActionType.Reaction,
            uses=uses,
            description=description,
        )

        return stats, feature


class _TailSwipe(Power):
    def __init__(self):
        super().__init__(name="Tail Swipe", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        tail_attack = stats.attack.scale(
            scalar=0.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            name="Tail Attack",
            attack_type=AttackType.MeleeNatural,
            reach=10,
            additional_description="On a hit, the target is pushed up to 10 feet away.",
        )

        stats = stats.add_attack(tail_attack)

        feature = Feature(
            name="Tail Swipe",
            action=ActionType.Reaction,
            description=f"When a creature {stats.selfref} can see within 10 feet hits {stats.selfref} with a melee attack, {stats.selfref} makes a Tail Attack against it.",
        )
        return stats, feature


class _WingBuffet(Power):
    def __init__(self):
        super().__init__(name="Tail Swipe", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate, high_cr_boost=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(speed=stats.speed.grant_flying())
        dmg = DieFormula.target_value(0.5 * stats.attack.average_damage, suggested_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Wing Buffet",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} beats its wings. Each other creature within 10 feet must make a DC {dc} Strength saving throw. \
                On a failure, the creature takes {dmg.description} bludgeoning damage and is knocked **Prone**. On a success, the creature takes half damage and is not knocked prone. \
                The dragon then flies up to half its movement speed. This movement does not trigger attacks of opportunity from prone targets.",
        )
        return stats, feature


class _DragonsGreed(Power):
    def __init__(self):
        super().__init__(name="Dragon's Greed", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Dragon's Greed",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} targets a creature it can see within 60 feet, preferring to target the creature in posession of the most valuable treasure or magical items. \
                The creature must make a DC {dc} Charisma saving throw or be **Charmed** by {stats.selfref} (save ends at end of turn). While charmed in this way, the creature must use its movement and action \
                to approach {stats.selfref} and make it an offering of its most valuable treasure or magical item. The target uses its action to place the offering on the floor at its feet.",
        )
        return stats, feature


class _DraconicMinions(Power):
    def __init__(self):
        super().__init__(name="Draconic Minions", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_dragon(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        desired_summon_cr = ceil(stats.cr / 2.5)

        _, _, description = summoning.determine_summon_formula(
            summon_list=stats.creature_type,
            summon_cr_target=desired_summon_cr,
            rng=rng,
        )

        feature = Feature(
            name="Draconic Minions",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} roars, summoning its minions to its aid. {description}",
        )

        return stats, feature


DragonsGaze: Power = _DragonsGaze()
DragonsGreed: Power = _DragonsGreed()
DraconicMinions: Power = _DraconicMinions()
DraconicRetaliation: Power = _DraconicRetaliation()
TailSwipe: Power = _TailSwipe()
WingBuffet: Power = _WingBuffet()


DragonPowers: List[Power] = [
    BreathAttack,
    DragonsGaze,
    DragonsGreed,
    DraconicMinions,
    DraconicRetaliation,
    TailSwipe,
    WingBuffet,
]
