from math import ceil, floor
from typing import Dict, List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural as natural_attacks
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five, summoning
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import AttackNames, score


def score_dragon(
    candidate: BaseStatblock,
    high_cr_boost: bool = False,
    attack_names: AttackNames = None,
    require_secondary_damage_type: bool = False,
) -> float:
    def has_secondary_damage_type(b: BaseStatblock) -> bool:
        return not require_secondary_damage_type or b.secondary_damage_type is not None

    return score(
        candidate=candidate,
        require_types=CreatureType.Dragon,
        require_callback=has_secondary_damage_type,
        require_cr=2,
        bonus_cr=7 if high_cr_boost else None,
        attack_names=attack_names,
    )


class _DragonsGaze(PowerBackport):
    def __init__(self):
        super().__init__(name="Dragon's Gaze", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_dragon(candidate)

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


class _DraconicRetaliation(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Draconic Retaliation", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_dragon(candidate, high_cr_boost=True)

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


class _TailSwipe(PowerBackport):
    def __init__(self):
        super().__init__(name="Tail Swipe", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_dragon(candidate, attack_names=natural_attacks.Tail)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = stats.add_attack(
            scalar=0.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            name="Tail Attack",
            attack_type=AttackType.MeleeNatural,
            reach=10,
            additional_description="On a hit, the target is pushed up to 10 feet away.",
        )

        feature = Feature(
            name="Tail Swipe",
            action=ActionType.Reaction,
            description=f"When a creature {stats.selfref} can see within 10 feet hits {stats.selfref} with a melee attack, {stats.selfref} makes a Tail Attack against it.",
        )
        return stats, feature


class _WingBuffet(PowerBackport):
    def __init__(self):
        super().__init__(name="Tail Swipe", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_dragon(candidate, high_cr_boost=True)

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


class _DragonsGreed(PowerBackport):
    def __init__(self):
        super().__init__(name="Dragon's Greed", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        return score_dragon(candidate)

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


class _DraconicMinions(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Draconic Minions", power_type=PowerType.Creature, power_level=HIGH_POWER
        )

    def check_minions(self, stats: BaseStatblock, rng: np.random.Generator) -> str | None:
        desired_summon_cr = stats.cr / 2.5
        damage_type = stats.secondary_damage_type
        if damage_type is None:
            return None

        try:
            _, _, description = summoning.determine_summon_formula(
                summoner=[stats.creature_type, damage_type],
                summon_cr_target=desired_summon_cr,
                rng=rng,
            )
            return description
        except ValueError:
            return None

    def score(self, candidate: BaseStatblock) -> float:
        minions = self.check_minions(candidate, np.random.default_rng())
        if minions is None:
            return -1

        return score_dragon(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type
        if damage_type is None:
            raise ValueError("dragon does not have a secondary damage type")

        description = self.check_minions(stats, rng)
        if description is None:
            raise ValueError("Dragon has no minions available")

        feature = Feature(
            name="Draconic Minions",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} roars, summoning its minions to its aid. {description}",
        )

        return stats, feature


class _DragonsBreath(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Breath Attack", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return 2 * score_dragon(candidate, high_cr_boost=True)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type or DamageType.Fire

        if stats.cr <= 3:
            distance = 15
        elif stats.cr <= 7:
            distance = 30
        elif stats.cr <= 11:
            distance = 45
        else:
            distance = 60

        if rng.random() <= 0.5:
            template = f"{distance} ft cone"
            save_type = "Constitution"
            multiplier = 1
        else:
            width = easy_multiple_of_five(5 * distance / 15)
            template = f"{2*distance} ft line {width} ft wide"
            save_type = "Dexterity"
            multiplier = 1.1

        dmg = DieFormula.target_value(
            max(
                5 + multiplier * 2 * stats.cr,
                multiplier * 3.8 * stats.cr,
                multiplier * 0.6 * stats.attack.average_damage * stats.multiattack,
            ),
            suggested_die=Die.d8,
        )

        dc = stats.difficulty_class

        feature = Feature(
            name=f"{damage_type.capitalize()} Breath",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} breathes {damage_type} in a {template}. \
                Each creature in the area must make a DC {dc} {save_type} save. \
                On a failure, the creature takes {dmg.description} {damage_type} damage or half as much on a success.",
        )

        return stats, feature


DragonsBreath: Power = _DragonsBreath()
DragonsGaze: Power = _DragonsGaze()
DragonsGreed: Power = _DragonsGreed()
DraconicMinions: Power = _DraconicMinions()
DraconicRetaliation: Power = _DraconicRetaliation()
TailSwipe: Power = _TailSwipe()
WingBuffet: Power = _WingBuffet()


DragonPowers: List[Power] = [
    DragonsBreath,
    DragonsGaze,
    DragonsGreed,
    DraconicMinions,
    DraconicRetaliation,
    TailSwipe,
    WingBuffet,
]
