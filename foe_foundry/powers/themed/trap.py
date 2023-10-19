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
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import choose_enum, easy_multiple_of_five
from ..attack import flavorful_damage_types
from ..power import Power, PowerBackport, PowerType
from ..utils import score


def score_trap(candidate: BaseStatblock) -> float:
    # these powers make sense for creatures that are capable of using equipment
    creature_types = {c for c in CreatureType if c.could_use_equipment}

    return score(
        candidate=candidate,
        require_types=creature_types,
        bonus_types=CreatureType.Humanoid,
        bonus_roles={MonsterRole.Leader, MonsterRole.Ambusher},
        bonus_skills=Skills.Survival,
    )


class _Snare(PowerBackport):
    def __init__(self):
        super().__init__(name="Snare", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_trap(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        quantity = ceil(stats.cr / 3)

        feature = Feature(
            name="Snares",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is a skilled trapper. Unless surprised, {stats.selfref} has placed up to {quantity} snares in its vicinity. \
                When a creature moves within 15 feet of the snare, if it has a passive perception of {dc} or higher it becomes aware of the snare. \
                The snares can also actively be detected by a creature within 30 feet using an action to make a DC {dc} Perception check. \
                A creature that is unaware of an untriggered snare and moves within 5 feet of it must make a DC {dc} Dexterity saving throw. \
                On a failure, it is lifted into the air and **Restrained** (escape DC {dc}).",
        )

        return stats, feature


class _SpikePit(PowerBackport):
    def __init__(self):
        super().__init__(name="Spike Pit", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_trap(candidate)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        dc = stats.difficulty_class
        quantity = ceil(stats.cr / 3)
        fall_damage = DieFormula.from_expression("2d6")
        spike_damage = DieFormula.target_value(
            0.5 * stats.attack.average_damage, force_die=Die.d6
        )

        feature = Feature(
            name="Spike Traps",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is a skilled trapper. Unless surprised, {stats.selfref} has placed up to {quantity} spike traps in its vicinity. \
                When a creature moves within 15 feet of the trap, if it has a passive perception of {dc} or higher it becomes aware of the trap. \
                The traps can also actively be detected by a creature within 30 feet using an action to make a DC {dc} Perception check. \
                A creature that moves within 5 feet of it must make a DC {dc} Dexterity saving throw or fall into the pit. \
                A creature that falls inside suffers {fall_damage.description} bludgeoning damage from the fall and {spike_damage.description} piercing damage from the spikes. \
                The pit is 10 feet deep and can be climbed out of using an action to perform a DC 12 Athletics check",
        )

        return stats, feature


Snare: Power = _Snare()
SpikePit: Power = _SpikePit()

TrapPowers: List[Power] = [Snare, SpikePit]
