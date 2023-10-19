from math import ceil, floor
from typing import List, Tuple

import numpy as np

from ...attack_template import natural, spell, weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import Power, PowerBackport, PowerType
from ..utils import score


def _score(candidate: BaseStatblock) -> float:
    return score(
        candidate=candidate,
        require_types=[CreatureType.Plant, CreatureType.Aberration, CreatureType.Monstrosity],
        bonus_damage=DamageType.Poison,
        require_no_other_damage_type=True,
        attack_modifiers=[
            "-",
            weapon.Daggers,
            weapon.Shortswords,
            weapon.RapierAndShield,
            weapon.Crossbow,
            weapon.Longbow,
            weapon.Shortbow,
            natural.Bite,
            natural.Claw,
            natural.Stinger,
            natural.Tentacle,
            spell.Poisonbolt,
        ],
    )


class _PoisonousDemise(PowerBackport):
    def __init__(self):
        super().__init__(name="Poisonous Demise", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        stats = stats.copy(secondary_damage_type=DamageType.Poison)

        dmg = DieFormula.target_value(2 + stats.cr, force_die=Die.d6)
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 4, min_val=10, max_val=60)

        feature = Feature(
            name="Poisonous Demise",
            description=f"When {stats.selfref} dies, they release a spray of poison. Each creature within {distance} ft must succeed on a DC {dc} Constitution save or take {dmg.description} poison damage",
            action=ActionType.Reaction,
        )

        return stats, feature


class _VirulentPoison(PowerBackport):
    def __init__(self):
        super().__init__(name="Virulent Poison", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return _score(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        stats = stats.copy(secondary_damage_type=DamageType.Poison)

        feature1 = Feature(
            name="Virulent Poison",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s attacks that deal poison damage ignore a target's resistance to poison damage. \
                If a target has immunity to poison damage, it instead has resistance to poison damage against this creature's attacks.",
        )

        feature2 = Feature(
            name="Virulent Poison",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description="On a hit, the target is **Poisoned** until the end of their next turn.",
        )

        return stats, [feature1, feature2]


PoisonousDemise: Power = _PoisonousDemise()
VirulentPoison: Power = _VirulentPoison()

PoisonPowers: List[Power] = [PoisonousDemise, VirulentPoison]
