from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..attack_modifiers import resolve_attack_modifier
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def _score_could_be_reckless_fighter(
    candidate: BaseStatblock, large_size_boost: bool = False, allow_defender: bool = False
) -> float:
    def is_reckless(c: BaseStatblock) -> bool:
        if not allow_defender and c.role == MonsterRole.Defender:
            return False
        elif c.attributes.WIS >= 12:
            return False
        else:
            return True

    return score(
        candidate=candidate,
        require_attack_types=AttackType.AllMelee(),
        require_callback=is_reckless,
        bonus_roles=MonsterRole.Bruiser,
        bonus_size=Size.Large if large_size_boost else None,
        attack_modifiers=[
            natural.Claw,
            natural.Bite,
            natural.Tail,
            natural.Lob,
            natural.Slam,
            weapon.Greataxe,
            weapon.Greatsword,
            weapon.Maul,
        ],
    )


def _as_reckless_fighter(stats: BaseStatblock, uses_weapon: bool = False) -> BaseStatblock:
    new_attrs = stats.attributes.copy(primary_attribute=Stats.STR)

    changes: dict = dict(attributes=new_attrs)
    if uses_weapon:
        changes.update(attack_type=AttackType.MeleeWeapon)
    return stats.copy(**changes)


class _Charger(PowerBackport):
    def __init__(self):
        super().__init__(name="Charger", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, large_size_boost=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        dc = stats.difficulty_class
        feature = Feature(
            name="Charge",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} charges and moves up to its speed. Up to one creature that is within 5 ft of the path \
                that the creature charges must make a DC {dc} Strength saving throw or be knocked **Prone**.",
        )
        return stats, feature


class _Frenzy(PowerBackport):
    """Frenzy (Trait). At the start of their turn, this creature can gain advantage on all melee weapon attack rolls made during this
    turn, but attack rolls against them have advantage until the start of their next turn."""

    def __init__(self):
        super().__init__(name="Frenzy", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        feature = Feature(
            name="Frenzy",
            description=f"At the start of their turn, {stats.selfref} can gain advantage on all melee weapon attack rolls made during this turn, but attack rolls against them have advantage until the start of their next turn.",
            action=ActionType.Feature,
        )
        return stats, feature


class _RefuseToSurrender(PowerBackport):
    """When this creature’s current hit points are below half their hit point maximum,
    the creature deals CR extra damage with each of their attacks."""

    def __init__(self):
        super().__init__(
            name="Refuse to Surrender", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(
            candidate, large_size_boost=True, allow_defender=True
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        threshold = easy_multiple_of_five(stats.hp.average / 2.0)
        dmg = DieFormula.target_value(0.75 * stats.cr, force_die=Die.d6)
        feature = Feature(
            name="Refuse to Surrender",
            description=f"When {stats.selfref}'s current hit points are below {threshold}, the creature deals an extra {dmg.description} damage with each of its attacks.",
            action=ActionType.Feature,
        )
        return stats, feature


class _GoesDownFighting(PowerBackport):
    """When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious."""

    def __init__(self):
        super().__init__(
            name="Goes Down Fighting", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _WildCleave(PowerBackport):
    def __init__(self):
        super().__init__(name="Wild Cleave", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        reach = stats.attack.reach or 5 + 5
        push = 2 * reach

        feature = Feature(
            name="Wild Cleave",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes an attack against every creature within {reach} ft. On a hit, the creature is pushed up to {push} feet away.",
        )

        return stats, feature


class _FlurryOfBlows(PowerBackport):
    def __init__(self):
        super().__init__(name="Flurry of Blows", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(candidate, allow_defender=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        attacks = max(3, int(ceil(1.5 * stats.multiattack)))
        attack_name = stats.attack.name

        feature = Feature(
            name="Flurry of Blows",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} makes a reckless flurry of {attacks} {attack_name}. Attacks against {stats.selfref} have advantage until the end of {stats.selfref}'s next turn.",
        )

        return stats, feature


class _Toss(PowerBackport):
    def __init__(self):
        super().__init__(name="Toss", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score_could_be_reckless_fighter(
            candidate, allow_defender=False, large_size_boost=True
        )

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        stats = _as_reckless_fighter(stats)
        size = stats.size.decrement()
        dmg = DieFormula.target_value(0.7 * stats.attack.average_damage, force_die=Die.d6)
        distance = easy_multiple_of_five(3 * stats.cr, min_val=10, max_val=30)
        dc = stats.difficulty_class

        feature = Feature(
            name="Toss",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} attempts to toss a {size} or smaller creature within 5 feet. The creature must make a DC {dc} Strength saving throw. \
                On a failure, it takes {dmg.description} bludgeoning damage and is thrown up to {distance} feet and falls **Prone**. If the thrown creature collides with another creature, then that other creature must make a DC {dc} Dexterity saving throw. \
                On a failure, the other creature takes half the damage.",
        )

        return stats, feature


Charger: Power = _Charger()
Frenzy: Power = _Frenzy()
FlurryOfBlows: Power = _FlurryOfBlows()
GoesDownFighting: Power = _GoesDownFighting()
RefuseToSurrender: Power = _RefuseToSurrender()
Toss: Power = _Toss()
WildCleave: Power = _WildCleave()


RecklessPowers: List[Power] = [
    Charger,
    Frenzy,
    FlurryOfBlows,
    GoesDownFighting,
    RefuseToSurrender,
    Toss,
    WildCleave,
]
