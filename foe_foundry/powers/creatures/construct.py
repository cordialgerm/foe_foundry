from math import ceil
from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock, MonsterDials
from ..power import Power, PowerType
from ..scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Sentinel(Power):
    """Sentinel (Trait). This creature can make opportunity attacks without using a reaction."""

    def __init__(self):
        super().__init__(name="Sentinel", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Construct:
            return NO_AFFINITY
        else:
            return HIGH_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Sentinel",
            action=ActionType.Feature,
            description="This creature can make opportunity attacks without using a reaction.",
        )

        return stats, feature


class _ArmorPlating(Power):
    """Armor Plating (Trait). This creature has a +2 bonus to Armor Class.
    Each time the creature's hit points are reduced by one-quarter of their maximum value,
    this bonus decreases by 1, to a maximum penalty to Armor Class of -2."""

    def __init__(self):
        super().__init__(name="Armor Plating", power_type=PowerType.Creature)

    def score(self, candidate: BaseStatblock) -> float:
        if candidate.creature_type != CreatureType.Construct:
            return NO_AFFINITY

        return HIGH_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        stats = stats.apply_monster_dials(MonsterDials(ac_modifier=2))

        hp = 5 * ceil(0.2 * stats.hp.average / 5.0)

        feature = Feature(
            name="Armor Plating",
            action=ActionType.Feature,
            description=f"This creature has a +2 bonus to AC (included in AC). \
                Each time it takes {hp} or more damage in a single turn its AC is reduced by 1",
        )

        return stats, feature


Sentinel: Power = _Sentinel()
ArmorPlating: Power = _ArmorPlating()

ConstructPowers: List[Power] = [ArmorPlating, Sentinel]

# TODO
# Explosive Core
# Beam Attack
# Spell Reflection
# Spell Storing
