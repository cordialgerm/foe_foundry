from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_ghoul(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Ghoul"


class GhoulPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="ghoul",
            reference_statblock="Ghoul",
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            icon=icon,
            power_types=power_types,
            score_args=dict(
                require_callback=is_ghoul,
                require_types=CreatureType.Undead,
            )
            | score_args,
        )


class _Cannibal(GhoulPower):
    def __init__(self):
        super().__init__(
            name="Cannibal",
            source="Foe Foundry",
            icon="eating",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 20),
            power_types=[PowerType.Healing],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(2 * stats.cr, min_val=5, max_val=50)

        feature = Feature(
            name="Cannibal",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} consumes the flesh of a corpse within 5 feet. It gains {temp_hp} temporary hitpoints.",
        )
        return [feature]


Cannibal: Power = _Cannibal()
GhoulPowers: list[Power] = [Cannibal]
