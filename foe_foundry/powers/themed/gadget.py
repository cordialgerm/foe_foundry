from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import choose_enum, easy_multiple_of_five
from ..attack import flavorful_damage_types
from ..power import Power, PowerBackport, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


def _score_gadget(
    candidate: BaseStatblock, require_living: bool = False, ignore_casters: bool = False
) -> float:
    # these powers make sense for creatures that are capable of using equipment
    if not candidate.creature_type.could_use_equipment:
        return NO_AFFINITY
    elif require_living and not candidate.creature_type.is_living:
        return NO_AFFINITY
    elif ignore_casters and candidate.attack_type.is_spell():
        return NO_AFFINITY

    creature_types = {
        CreatureType.Humanoid: MODERATE_AFFINITY,
        CreatureType.Giant: MODERATE_AFFINITY,
    }

    roles = {
        MonsterRole.Leader: MODERATE_AFFINITY,
        MonsterRole.Controller: MODERATE_AFFINITY,
        MonsterRole.Ambusher: MODERATE_AFFINITY,
        MonsterRole.Defender: LOW_AFFINITY,
    }

    score = creature_types.get(candidate.creature_type, LOW_AFFINITY)
    score += roles.get(candidate.role, 0)
    return score


class _HealingPotions(PowerBackport):
    def __init__(self):
        super().__init__(name="Healing Potions", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_gadget(candidate, require_living=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        if stats.cr <= 3:
            name = "Potion of Healing"
            healing = DieFormula.from_expression("2d4 + 2")
        elif stats.cr <= 7:
            name = "Potion of Greater Healing"
            healing = DieFormula.from_expression("4d4 + 4")
        elif stats.cr <= 11:
            name = "Potion of Superior Healing"
            healing = DieFormula.from_expression("8d4 + 8")
        else:
            name = "Potion of Supreme Healing"
            healing = DieFormula.from_expression("10d4 + 10")

        uses = int(ceil(min(3, stats.cr / 8)))

        feature = Feature(
            name=name,
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} consumes a {name} and regains {healing.description} hitpoints",
        )

        return stats, feature


class _SmokeBomb(PowerBackport):
    def __init__(self):
        super().__init__(name="Smoke Bomb", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_gadget(candidate, ignore_casters=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        distance = easy_multiple_of_five(5 + stats.cr / 5, min_val=10, max_val=30)
        rounds = DieFormula.from_expression("1d4 + 2")

        feature = Feature(
            name="Smoke Bomb",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} throws a smoke bomb at a point they can see within 30 feet. A thick obscuring cloud of smoke billows forth and fills a {distance} ft radius sphere. \
                The smoke lasts for {rounds.description} rounds and can be dispersed with a light wind.",
        )

        return stats, feature


class _Net(PowerBackport):
    def __init__(self):
        super().__init__(name="Net", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_gadget(candidate, ignore_casters=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        distance = easy_multiple_of_five(stats.cr, min_val=5, max_val=15)
        dmg = int(ceil(0.25 * stats.attack.average_damage))

        if stats.cr <= 3:
            name = "Net"
            additional = ""
            ac = 10
            hp = 10
        elif stats.cr <= 7:
            name = "Barbed Net"
            additional = f" Whenever a creature uses an action to break the grapple or attack the net, they suffer {dmg} piercing damage"
            ac = 12
            hp = 15
        elif stats.cr <= 11:
            name = "Grounding Net"
            additional = f" Whenever a creature attempts to cast a spell while grappled in this way, they must succeed on a DC {dc} concentration check. On a failure, the spell fails."
            ac = 14
            hp = 20
        else:
            dmg_type = stats.secondary_damage_type or DamageType.Lightning
            name = f"{dmg_type.capitalize()}-Infused Net"
            ac = 16
            hp = 25
            additional = f" A creature grappled in this way suffers {dmg} ongoing {dmg_type} damage at the start of each of its turn, \
                and whenever the creature attempts to cast a spell it must succeed on a DC {dc} concentration check. On a failure, the spell fails."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} throws a net at a point they can see within 30 feet. Each creature within {distance} feet must make a DC {dc} Strength save. \
                On a failure, they are **Grappled** (escape DC {dc}) and **Restrained** while grappled in this way. The net has AC {ac} and {hp} hp.{additional}",
        )

        return stats, feature


class _MagicalExplosive(PowerBackport):
    def __init__(self):
        super().__init__(name="Net", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_gadget(candidate, ignore_casters=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        damage_types = flavorful_damage_types(stats, default=DamageType.Fire) | {
            DamageType.Fire
        }
        damage_type = choose_enum(rng=rng, values=list(damage_types))
        dmg = DieFormula.target_value(1.25 * stats.attack.average_damage, suggested_die=Die.d6)
        radius = 15
        distance = 30
        dc = stats.difficulty_class_easy

        name = f"{damage_type.capitalize()} Grenade"

        feature = Feature(
            name=name,
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} hurls a {name} at a point they can see within {distance} ft. The grenade explodes in a {radius} ft sphere. \
                Each creature in the area must make a DC {dc} Dexterity saving throw or take {dmg.description} {damage_type} damage. On a success, the creature takes half as much damage.",
        )

        return stats, feature


HealingPotions: Power = _HealingPotions()
MagicalExplosive: Power = _MagicalExplosive()
Net: Power = _Net()
SmokeBomb: Power = _SmokeBomb()


GadgetPowers: List[Power] = [HealingPotions, MagicalExplosive, Net, SmokeBomb]
