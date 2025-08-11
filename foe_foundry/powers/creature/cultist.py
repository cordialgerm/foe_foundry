from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...die import Die
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, MEDIUM_POWER, PowerCategory, PowerWithStandardScoring


def is_cultist(s: BaseStatblock) -> bool:
    return s.creature_class == "Cultist"


class CultistPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 5, 23),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="cultist",
            icon=icon,
            reference_statblock="Cultist",
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            power_types=power_types,
            score_args=dict(
                require_callback=is_cultist,
                require_types=[CreatureType.Humanoid],
            )
            | score_args,
        )


class _PyramidScheme(CultistPower):
    def __init__(self):
        def require_callback(s: BaseStatblock) -> bool:
            return (
                is_cultist(s)
                and MonsterRole.Leader not in s.additional_roles
                and s.cr < 1
            )

        super().__init__(
            name="Pyramid Scheme",
            source="Foe Foundry",
            icon="great-pyramid",
            power_level=LOW_POWER,
            require_max_cr=0.5,
            require_callback=require_callback,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Pyramid Scheme",
            action=ActionType.Feature,
            description=f"If another {stats.name} died last turn, then {stats.selfref} has advantage on d20 tests.",
        )
        return [feature]


class _SacrificialPawns(CultistPower):
    def __init__(self):
        def require_callback(s: BaseStatblock) -> bool:
            return (
                is_cultist(s)
                and MonsterRole.Leader not in s.additional_roles
                and s.cr < 1
            )

        super().__init__(
            name="Sacrificial Pawns",
            source="Foe Foundry",
            icon="sacrificial-dagger",
            power_level=LOW_POWER,
            require_max_cr=0.5,
            require_callback=require_callback,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Sacrificial Pawns",
            action=ActionType.Feature,
            description=f"When {stats.selfref} dies, if there is another higher-CR cultist within 60 feet, then that cultist gains temporary hit points equal to its CR.",
        )
        return [feature]


class _Indoctrination(CultistPower):
    def __init__(self):
        super().__init__(
            name="Indoctrination",
            source="Foe Foundry",
            icon="kneeling",
            power_level=MEDIUM_POWER,
            require_max_cr=0.5,
            require_callback=is_cultist,
            power_types=[PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = "1" if stats.cr < 1 else stats.target_value(target=0.25, force_die=Die.d4)
        cause = (
            "re-roll the attack roll" if stats.cr < 1 else "cause that attack to hit"
        )
        feature = Feature(
            name="Indoctrination",
            action=ActionType.BonusAction,
            uses=1,
            description=f"If {stats.selfref} missed an attack, it can instead {cause} and deal an additional {dmg} necrotic damage.",
        )
        return [feature]


SacrificialPawns = _SacrificialPawns()
Indoctrination = _Indoctrination()
PyramidScheme = _PyramidScheme()

CultistPowers = [
    Indoctrination,
    PyramidScheme,
    SacrificialPawns,
]
