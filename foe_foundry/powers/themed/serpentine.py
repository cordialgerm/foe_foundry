from datetime import datetime
from typing import List

from foe_foundry.features import ActionType, Feature
from foe_foundry.statblocks.base import BaseStatblock

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class _SerpentinePower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = MEDIUM_POWER):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="serpentine",
            power_level=power_level,
            power_type=PowerType.Theme,
            create_date=datetime(2025, 3, 14),
            score_args=dict(
                require_types=[CreatureType.Monstrosity, CreatureType.Beast],
                require_damage=DamageType.Poison,
            ),
        )


class _SerpentineHiss(_SerpentinePower):
    def __init__(self):
        super().__init__(
            name="Serpentine Hiss",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        frightened = Condition.Frightened
        dc = stats.difficulty_class
        feature = Feature(
            name="Serpentine Hiss",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} hisses menacingly. Each hostile creature within 30 feet must make a DC {dc} Wisdom save or be {frightened.caption} (save ends at end of turn). A creature that succeeds on the save is immune to this effect for 24 hours.",
        )

        return [feature]


SerpentineHiss: Power = _SerpentineHiss()


SerpentinePowers: list[Power] = [SerpentineHiss]
