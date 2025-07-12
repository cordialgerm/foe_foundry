from datetime import datetime
from typing import List

from foe_foundry.references import creature_ref

from ...creature_types import CreatureType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class GuardPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        existing_callback = score_args.pop("require_callback", None)

        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Guard" and (
                existing_callback(s) if existing_callback else True
            )

        super().__init__(
            name=name,
            source=source,
            theme="guard",
            icon=icon,
            reference_statblock="Guard",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=require_callback,
                require_types=[CreatureType.Humanoid],
            )
            | score_args,
        )


class _ProtectTheTarget(GuardPower):
    def __init__(self):
        super().__init__(
            name="Protect the Target",
            source="Foe Foundry",
            icon="shield-bounces",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Protect the Target",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack roles against creatures that have attacked or harmed what {stats.selfref} is guarding.",
        )
        return [feature]


class _SoundTheAlarm(GuardPower):
    def __init__(self):
        super().__init__(
            name="Sound the Alarm",
            source="Foe Foundry",
            icon="whistle",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(
            stats.target_value(target=0.5).average, min_val=5
        )

        feature = Feature(
            name="Sound the Alarm",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=True,
            description=f"{stats.selfref.capitalize()} sounds the alarm if the alarm hasn't already been sounded. Each friendly creature that can hear the alarm within 60 feet gains {temphp} temporary hitpoints",
        )
        return [feature]


class _DefensiveFormation(GuardPower):
    def __init__(self):
        super().__init__(
            name="Defensive Formation",
            source="Foe Foundry",
            icon="shield-echoes",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Defensive Formation",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack roles if it has partial or full cover.",
        )
        return [feature]


class _CallReinforcements(GuardPower):
    def __init__(self):
        super().__init__(
            name="Call Reinforcements",
            source="Foe Foundry",
            icon="megaphone",
            power_level=HIGH_POWER,
            create_date=datetime(2025, 2, 23),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        target = DieFormula.target_value(
            target=12 * (0.3 + stats.cr / 3), force_die=Die.d4
        )
        guard = creature_ref("Guard")

        feature = Feature(
            name="Call Reinforcements",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=True,
            description=f"{stats.selfref.capitalize()} summons {target.description} additional {guard} that arrive in 1d4 rounds. This ability can only be used once per combat by any guard in the encounter.",
        )
        return [feature]


ProtectTheTarget: Power = _ProtectTheTarget()
SoundTheAlarm: Power = _SoundTheAlarm()
DefensiveFormation: Power = _DefensiveFormation()
CallReinforcements: Power = _CallReinforcements()

GuardPowers: list[Power] = [
    CallReinforcements,
    DefensiveFormation,
    ProtectTheTarget,
    SoundTheAlarm,
]
