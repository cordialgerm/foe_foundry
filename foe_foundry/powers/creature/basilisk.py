from datetime import datetime
from typing import List

from foe_foundry.utils.summoning import summon_description

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    EXTRA_HIGH_POWER,
    HIGH_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class _BasiliskPower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = HIGH_POWER):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Basilisk"

        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="basilisk",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 3, 14),
            score_args=dict(
                require_callback=require_callback,
                bonus_types=CreatureType.Monstrosity,
                bonus_damage=DamageType.Poison,
            ),
        )


class _BasiliskBrood(_BasiliskPower):
    def __init__(self):
        super().__init__(name="Basilisk Brood", power_level=EXTRA_HIGH_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        description = summon_description(
            summoner=stats.selfref,
            summon="Basilisk",
            formula=DieFormula.from_expression("1d4"),
        )

        feature = Feature(
            name="Summon Brood",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} lets out a piercing cry for aid. {description}",
        )

        return [feature]


class _BasiliskGaze(_BasiliskPower):
    def __init__(
        self,
    ):
        super().__init__(
            name="Basilisk Gaze",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        petrified = Condition.Petrified
        restrained = Condition.Restrained
        dc = stats.difficulty_class_easy

        feature2 = Feature(
            name="Petrifying Gaze",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Each creature in a 30-foot cone must succeed on a DC {dc} Constitution saving throw. \
                On a failed save, the creature is {restrained.caption} and repeats the save at the end of its next turn. \
                If the creature is still {restrained.caption} at the end of its next turn, it is {petrified.caption}.",
        )

        return [feature2]


BasiliskBrood: Power = _BasiliskBrood()
BasiliskGaze: Power = _BasiliskGaze()

BasiliskPowers: list[Power] = [BasiliskBrood, BasiliskGaze]
