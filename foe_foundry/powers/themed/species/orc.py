from datetime import datetime
from typing import List

from ....creature_types import CreatureType
from ....damage import AttackType
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
from ...roles.bruiser import StunningBlow
from ..reckless import RelentlessEndurance


class OrcPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def is_orc(stats: BaseStatblock) -> bool:
            return (
                stats.creature_subtype is not None
                and stats.creature_subtype.lower() == "orc"
            )

        standard_score_args = dict(
            require_types=CreatureType.Humanoid,
            require_callback=is_orc,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Orc",
            score_args=standard_score_args,
        )


class OrcPowerWrapper(OrcPower):
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


class _Bloodrage(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodrage",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 17),
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Ambusher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bloodrage",
            description="The orc takes the Dash action as a bonus action and moves directly towards an enemy. The next attack it makes this turn is made with advantage.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _BloodrageBarrage(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodrage Barrage",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 17),
            require_attack_types=AttackType.AllRanged(),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bloodrage Barrage",
            description="When the orc misses with a ranged attack, it can make another ranged attack at the same target using its reaction. The attack is made with advantage.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


Bloodrage: Power = _Bloodrage()
BloodrageBarrage: Power = _BloodrageBarrage()
BloodrageBlow: Power = OrcPowerWrapper(
    name="Bloodrage Blow",
    source="Foe Foundry",
    wrapped_power=StunningBlow,
    create_date=datetime(2025, 2, 17),
    require_attack_types=AttackType.AllMelee(),
    bonus_roles=[MonsterRole.Bruiser],
)
BloodrageEndurance: Power = OrcPowerWrapper(
    name="Bloodrage Endurance",
    source="Foe Foundry",
    wrapped_power=RelentlessEndurance,
    create_date=datetime(2025, 2, 17),
    bonus_roles=[MonsterRole.Defender, MonsterRole.Bruiser, MonsterRole.Leader],
)

OrcPowers: List[Power] = [
    Bloodrage,
    BloodrageBarrage,
    BloodrageBlow,
    BloodrageEndurance,
]
