from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class _GorgonPower(PowerWithStandardScoring):
    def __init__(self, name: str, icon: str, power_level: float = MEDIUM_POWER):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Gorgon"

        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="gorgon",
            icon=icon,
            reference_statblock="Gorgon",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 3, 14),
            score_args=dict(
                require_callback=require_callback,
                bonus_types=CreatureType.Construct,
                bonus_damage=DamageType.Poison,
            ),
        )


class _PetrifyingBreath(_GorgonPower):
    def __init__(self):
        super().__init__(
            name="Petrifying Breath", icon="cloud-ring", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        restrained = Condition.Restrained
        petrified = Condition.Petrified
        dmg = stats.target_value(dpr_proportion=0.65, force_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Petrifying Breath",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} exhales poisonous petrifying gas in a 30-foot cone. Each creature in that area must make a DC {dc} Constitution saving throw. \
                     On a failed save, a creature takes {dmg.description} poison damage and is {restrained.caption} (save ends at end of turn). If the creature fails its second save, it is {petrified.caption}. \
                     On a successful save, the creature takes half damage instead.",
        )

        return [feature]


PetrifyingBreath: Power = _PetrifyingBreath()

GorgonPowers: list[Power] = [PetrifyingBreath]
