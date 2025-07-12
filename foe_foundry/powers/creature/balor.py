from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_balor(c: BaseStatblock) -> bool:
    return c.creature_class == "Balor"


class BalorPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str = "horned-skull",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = (
            dict(require_types=CreatureType.Fiend, require_callback=is_balor)
            | score_args
        )
        super().__init__(
            name=name,
            source=source,
            icon=icon,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            theme="Balor",
            reference_statblock="Balor",
            score_args=standard_score_args,
        )


class _FlameWhip(BalorPower):
    def __init__(self):
        super().__init__(
            name="Flame Whip",
            source="Foe Foundry",
            icon="whip",
            create_date=datetime(2025, 3, 3),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=1.3 if stats.multiattack >= 2 else 0.8)
        dc = stats.difficulty_class
        prone = Condition.Prone

        feature = Feature(
            name="Flame Whip",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} wraps a fiery whip around a creature within 30 feet. It must make a DC {dc} Dexterity save. \
                On a failure, it takes {dmg.description} fire damage and is pulled up to 30 feet closer to {stats.selfref} and is knocked {prone.caption}. On a success, it takes half damage instead.",
        )

        return [feature]


FlameWhip: Power = _FlameWhip()

BalorPowers = [
    FlameWhip,
]
