from datetime import datetime
from typing import List

from ....creature_types import CreatureType
from ....features import ActionType, Feature
from ....role_types import MonsterRole
from ....statblocks import BaseStatblock
from ...power import (
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)
from ...roles.defender import Taunt
from ..reckless import BloodiedRage


class DwarvenPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def is_dwarf(stats: BaseStatblock) -> bool:
            return (
                stats.creature_subtype is not None
                and stats.creature_subtype.lower() == "dwarf"
            )

        standard_score_args = dict(
            require_types=CreatureType.Humanoid,
            require_callback=is_dwarf,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Dwarf",
            score_args=standard_score_args,
        )


class DwarvenPowerWrapper(DwarvenPower):
    def __init__(
        self,
        name: str,
        source: str,
        wrapped_power: Power,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=wrapped_power.power_level,
            **score_args,
        )
        self.wrapped_power = wrapped_power

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return self.wrapped_power.generate_features(stats)

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return self.wrapped_power.modify_stats(stats)


class _HardDrink(DwarvenPower):
    def __init__(self):
        super().__init__(
            name="Hard Drink",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 17),
            bonus_roles=[MonsterRole.Bruiser],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Hard Drink",
            description=f"The dwarf can chug a strong dwarven drink and gain advantage on the next d20 test {stats.selfref} makes within the next hour.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _DwarvenResilience(DwarvenPower):
    def __init__(self):
        super().__init__(
            name="Dwarven Resilience",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            bonus_roles=[MonsterRole.Defender],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Dwarven Resilience",
            action=ActionType.Reaction,
            description="When the dwarf takes damage it may use its reaction to gain resistance to a damage type of its choice.",
            uses=1,
        )
        return [feature]


HardDrink: Power = _HardDrink()
DwarvenResilience: Power = _DwarvenResilience()
DwarvenTaunt: Power = DwarvenPowerWrapper(
    name="Dwarven Taunt",
    source="Foe Foundry",
    wrapped_power=Taunt,
    create_date=datetime(2025, 2, 17),
)
DwarvenRage: Power = DwarvenPowerWrapper(
    name="Dwarven Rage",
    source="Foe Foundry",
    wrapped_power=BloodiedRage,
    create_date=datetime(2025, 2, 17),
)

DwarfPowers: List[Power] = [
    HardDrink,
    DwarvenResilience,
    DwarvenTaunt,
    DwarvenRage,
]
