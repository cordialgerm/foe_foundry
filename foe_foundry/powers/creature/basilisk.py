from datetime import datetime
from typing import List

from foe_foundry.utils.summoning import summon_description

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import (
    EXTRA_HIGH_POWER,
    HIGH_POWER,
    LOW_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class _BasiliskPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        power_level: float = HIGH_POWER,
        icon: str | None = None,
        power_types: List[PowerType] | None = None,
    ):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Basilisk"

        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="basilisk",
            reference_statblock="Basilisk",
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=datetime(2025, 3, 14),
            power_types=power_types,
            score_args=dict(
                require_callback=require_callback,
                bonus_types=CreatureType.Monstrosity,
                bonus_damage=DamageType.Poison,
            ),
        )


class _BasiliskBrood(_BasiliskPower):
    def __init__(self):
        super().__init__(
            name="Basilisk Brood",
            power_level=EXTRA_HIGH_POWER,
            icon="egg-clutch",
            power_types=[PowerType.Summon],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        description = summon_description(
            summoner=stats.selfref,
            summon="Basilisk",
            formula=DieFormula.from_expression("1d4"),
        )

        feature = Feature(
            name="Basilisk Brood",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} lets out a piercing cry for aid. {description}",
        )

        return [feature]


class _StoneMolt(_BasiliskPower):
    def __init__(self):
        super().__init__(
            name="Stone Molt",
            icon="stegosaurus-scales",
            power_level=LOW_POWER,
            power_types=[PowerType.Defense, PowerType.Environmental],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Stone Molt",
            action=ActionType.Reaction,
            uses=1,
            description=f"When hit by an attack, {stats.selfref} violently molts its stone scales. It gains resistance to a damage type of its choice until the end of its next turn and the molted scales create difficult terrain for other creatures in a 10 foot radius around {stats.selfref}",
        )
        return [feature]


class _StoneEater(_BasiliskPower):
    def __init__(self):
        super().__init__(
            name="Stone Eater",
            icon="stone-pile",
            power_level=RIBBON_POWER,
            power_types=[PowerType.Healing, PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        petrified = Condition.Petrified
        feature = Feature(
            name="Stone Eater",
            action=ActionType.Feature,
            description=f"If {stats.selfref} deals damage to a {petrified.caption} creature, it regains that many hitpoints.",
        )
        return [feature]


BasiliskBrood: Power = _BasiliskBrood()
StoneMolt: Power = _StoneMolt()
StoneEater: Power = _StoneEater()

BasiliskPowers: list[Power] = [BasiliskBrood, StoneMolt, StoneEater]
