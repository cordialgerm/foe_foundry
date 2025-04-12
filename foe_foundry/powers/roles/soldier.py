from datetime import datetime
from typing import List

from ...damage import AttackType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class SoldierPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Soldier,
            bonus_attack_types=AttackType.AllMelee(),
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="soldier",
            score_args=standard_score_args,
        )


class _Phalanx(SoldierPower):
    def __init__(self):
        super().__init__(name="Phalanx", source="Foe Foundry", power_level=MEDIUM_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Phalanx",
            description=f"{stats.selfref.capitalize()} gains a +1 bonus to its AC and d20 tests whenever another ally with this trait is within 5 feet.",
            action=ActionType.Feature,
        )
        return [feature]


class _CoordinatedStrike(SoldierPower):
    def __init__(self):
        super().__init__(
            name="Coordinated Strike", source="Foe Foundry", power_level=MEDIUM_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Coordinated Strike",
            description=f"Whenever an ally within 5 feet misses an attack and {stats.selfref} is within 5 feet of the target, {stats.selfref} can use their reaction to make an attack against the target. \
                This ability can only trigger once per round for each such group of allies with this trait.",
            action=ActionType.Reaction,
        )
        return [feature]


CoordinatedStrike: Power = _CoordinatedStrike()
Phalanx: Power = _Phalanx()

SoldierPowers: list[Power] = [
    CoordinatedStrike,
    Phalanx,
]
