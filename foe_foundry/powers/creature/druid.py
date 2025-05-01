from typing import List

from ...attributes import Stats
from ...creature_types import CreatureType
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


def is_druid(c: BaseStatblock) -> bool:
    return c.creature_class == "Druid"


class DruidPower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = MEDIUM_POWER):
        super().__init__(
            name=name,
            power_type=PowerType.Species,
            power_level=power_level,
            source="Foe Foundry",
            theme="druid",
            reference_statblock="Druid",
            score_args=dict(
                require_callback=is_druid,
                require_types=CreatureType.Humanoid,
            ),
        )


class _BestialWrath(DruidPower):
    def __init__(self):
        super().__init__(
            name="Bestial Wrath",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(3 + 3 * stats.cr, min_val=5, max_val=100)
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=1.15, force_die=Die.d6)
        feature = Feature(
            name="Bestial Fury",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} temporarily transforms into a bestial form until the end of its turn and gains {temp_hp} hitpoints. \
                While in the form, it claws at a nearby creature within 10 feet. The creature must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg.description} slashing damage and is pushed back 10 feet. On a success, it takes half damage instead.",
        )
        return [feature]


class _PrimalEncouragement(DruidPower):
    def __init__(self):
        super().__init__(
            name="Primal Encouragement",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        healing = stats.target_value(
            0.5, force_die=Die.d4, flat_mod=stats.attributes.WIS
        )
        uses = stats.attributes.stat_mod(Stats.WIS)

        feature = Feature(
            name="Druidic Healing",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.roleref.capitalize()} utters a word of primal encouragement to a friendly ally it can see within 60 feet. \
                The ally regains {healing.description} hitpoints.",
        )

        return [feature]


BestialWrath: Power = _BestialWrath()
PrimalEncouragement: Power = _PrimalEncouragement()

DruidPowers: List[Power] = [
    BestialWrath,
    PrimalEncouragement,
]
