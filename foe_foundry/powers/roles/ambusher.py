from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...attributes import Skills, Stats
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from .. import flags
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


class AmbusherPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        reference_statblock: str = "Assassin",
        power_types: List[PowerType] | None = None,
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
            power_category=PowerCategory.Role,
            source=source,
            power_level=power_level,
            create_date=create_date,
            icon=icon,
            theme="Ambusher",
            reference_statblock=reference_statblock,
            power_types=power_types,
            score_args=standard_score_args,
        )


class _CunningAction(AmbusherPower):
    def __init__(self):
        super().__init__(
            name="Cunning Action",
            source="SRD5.1 Spy",
            reference_statblock="Spy",
            icon="running-ninja",
            power_types=[PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        disengage = action_ref("Disengage")
        hide = action_ref("Hide")
        feature = Feature(
            name="Cunning Action",
            description=f"{stats.roleref.capitalize()} uses {dash}, {disengage}, or {hide}.",
            action=ActionType.BonusAction,
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.copy(has_unique_movement_manipulation=True)


class _StealthySneak(AmbusherPower):
    def __init__(self):
        super().__init__(
            name="Stealthy Sneak",
            source="A5E SRD Bugbear",
            icon="cultist",
            create_date=datetime(2023, 11, 22),
            power_types=[PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hide = action_ref("Hide")
        feature = Feature(
            name="Stealthy Sneak",
            description=f"{stats.selfref.capitalize()} moves up to half its speed without provoking opportunity attacks. It can then attempt to {hide}.",
            action=ActionType.Action,
            replaces_multiattack=1,
        )
        return [feature]


class _DeadlyAmbusher(AmbusherPower):
    def __init__(self):
        super().__init__(
            name="Deadly Ambusher",
            source="SRD5.1 Assasin",
            icon="surprised",
            require_no_flags=flags.MODIFIES_CRITICAL,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Deadly Ambusher",
            description=f"On the first turn of combat, {stats.selfref} has advantage on any attack rolls against targets with lower initiative than it, \
                and it scores a critical hit on a score of 19 or 20.",
            action=ActionType.Feature,
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return (
            stats.grant_proficiency_or_expertise(Skills.Initiative)
            .grant_proficiency_or_expertise(Skills.Initiative)
            .with_flags(flags.MODIFIES_CRITICAL)
        )


CunningAction: Power = _CunningAction()
DeadlyAmbusher: Power = _DeadlyAmbusher()
StealthySneak: Power = _StealthySneak()

AmbusherPowers: List[Power] = [
    CunningAction,
    DeadlyAmbusher,
    StealthySneak,
]
