from datetime import datetime
from typing import List

from ...attributes import Skills, Stats
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring
from .shared import CunningAction as _CunningAction
from .shared import NimbleEscape as _NimbleEscape


class AmbusherPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Ambusher,
            bonus_stats=Stats.DEX,
            bonus_skills=Skills.Stealth,
            bonus_speed=40,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            source=source,
            power_level=power_level,
            create_date=create_date,
            theme="Ambusher",
            score_args=standard_score_args,
        )


class _StealthySneak(AmbusherPower):
    def __init__(self):
        super().__init__(
            name="Stealthy Sneak", source="A5E SRD Bugbear", create_date=datetime(2023, 11, 22)
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Stealthy Sneak",
            description=f"{stats.selfref.capitalize()} moves up to half its speed without provoking opportunity attacks. It can then attempt to hide.",
            action=ActionType.Action,
            replaces_multiattack=1,
        )
        return [feature]


class _DeadlyAmbusher(AmbusherPower):
    def __init__(self):
        super().__init__(name="Deadly Ambusher", source="SRD5.1 Assasin")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Deadly Ambusher",
            description=f"{stats.selfref.capitalize()} has advantage on initiative rolls. \
                On the first turn of combat, it has advantage on any attack rolls against targets with lower initiative than it, \
                and it scores a critical hit on a score of 19 or 20.",
            action=ActionType.Feature,
        )
        return [feature]


CunningAction: Power = _CunningAction(MonsterRole.Ambusher)
NimbleEscape: Power = _NimbleEscape(MonsterRole.Ambusher)
DeadlyAmbusher: Power = _DeadlyAmbusher()
StealthySneak: Power = _StealthySneak()

AmbusherPowers: List[Power] = [CunningAction, DeadlyAmbusher, NimbleEscape, StealthySneak]
