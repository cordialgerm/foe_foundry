from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import conditions
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_gelatinous_cube(s: BaseStatblock) -> bool:
    return s.creature_class == "Gelatinous Cube"


class GelatinousCubePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 4, 17),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="gelatinous_cube",
            icon="transparent-slime",
            reference_statblock="Gelatinous Cube",
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            power_types=power_types,
            score_args=dict(
                require_callback=is_gelatinous_cube,
                require_types=[CreatureType.Ooze],
            )
            | score_args,
        )


class _EngulfInOoze(GelatinousCubePower):
    def __init__(self):
        super().__init__(
            name="Engulf in Ooze",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            require_max_cr=1,
            power_types=[PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=0.75)
        dc = stats.difficulty_class
        engulfed = conditions.Engulfed(damage=dmg, escape_dc=dc)

        feature = Feature(
            name="Engulf in Ooze",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} moves up to its speed and can enter Large or smaller creature's spaces. \
                When it enters a creature's space, that creature must make a DC {dc} Dexterity save. \
                The save is made at disadvantage if the target is unaware of the cube, and automatically fails if there is no nearby unoccupied space. \
                <br/> On a failure, the creature takes {dmg.description} acid damage and is {engulfed.caption}. {engulfed.description_3rd}.",
        )
        return [feature]


class _MetabolicSurge(GelatinousCubePower):
    def __init__(self):
        super().__init__(
            name="Metabolic Surge",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            require_max_cr=1,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        engulfed = conditions.Engulfed(damage="1")
        hp = easy_multiple_of_five(stats.hp.average * 0.2)
        feature = Feature(
            name="Metabolic Surge",
            action=ActionType.BonusAction,
            description=f"If {stats.selfref} has at least 2 creatures {engulfed.caption} then it gains {hp} temporary hit points",
        )
        return [feature]


class _PerfectlyTransparant(GelatinousCubePower):
    def __init__(self):
        super().__init__(
            name="Perfectly Transparent",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            power_types=[PowerType.Defense, PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        engulfed = conditions.Engulfed(damage="1")
        invisible = conditions.Condition.Invisible
        feature = Feature(
            name="Perfectly Transparent",
            action=ActionType.BonusAction,
            description=f"If {stats.selfref} has no creatures {engulfed.caption} then it becomes {invisible.caption} until the beginning of its next turn.",
        )
        return [feature]


EngulfInOoze: Power = _EngulfInOoze()
MetabolicSurge: Power = _MetabolicSurge()
PerfectlyTransparent: Power = _PerfectlyTransparant()

GelatinousCubePowers: list[Power] = [
    EngulfInOoze,
    MetabolicSurge,
    PerfectlyTransparent,
]
