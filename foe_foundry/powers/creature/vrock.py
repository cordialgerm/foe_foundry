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
    PowerCategory,
    PowerWithStandardScoring,
)


class _VrockPower(PowerWithStandardScoring):
    def __init__(self, name: str, icon: str, power_level: float = MEDIUM_POWER):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Vrock"

        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="vrock",
            icon=icon,
            reference_statblock="Vrock",
            power_level=power_level,
            power_type=PowerCategory.Creature,
            create_date=datetime(2025, 3, 16),
            score_args=dict(
                require_callback=require_callback,
                bonus_types=CreatureType.Fiend,
                bonus_damage=DamageType.Poison,
            ),
        )


class _StunningScreech(_VrockPower):
    def __init__(self):
        super().__init__(
            name="Stunning Screech", icon="screaming", power_level=HIGH_POWER
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        stunned = Condition.Stunned
        dmg = stats.target_value(dpr_proportion=0.65, force_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Stunning Screech",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} lets loose an unholy screech. Each non-demon within 20 feet must make a DC {dc} Constitution save. \
                On a failure, the creature takes {dmg.description} Thunder damage and is {stunned.caption} until the end of its next turn. On a success, a creature takes half damage instead",
        )

        return [feature]


StunningScreech: Power = _StunningScreech()

VrockPowers: list[Power] = [StunningScreech]
