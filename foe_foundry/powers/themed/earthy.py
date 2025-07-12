from datetime import datetime
from typing import List

from ...attributes import Skills
from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class EarthPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Earth Elemental",
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=power_level,
            power_type=PowerCategory.Theme,
            theme="earth",
            icon=icon,
            reference_statblock=reference_statblock,
            score_args=dict(
                require_types=[
                    CreatureType.Beast,
                    CreatureType.Monstrosity,
                    CreatureType.Ooze,
                ],
            )
            | score_args,
        )


class _Burrower(EarthPower):
    def __init__(self):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return (
                not (c.speed.fly or 0)
                and not (c.speed.swim or 0)
                and not (c.speed.climb or 0)
            )

        super().__init__(
            name="Burrower",
            source="SRD5.1 Purple Worm",
            icon="dig-hole",
            power_level=RIBBON_POWER,
            require_callback=not_already_special_movement,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(burrow=stats.speed.walk)
        new_senses = stats.senses.copy(blindsight=60)

        stats = super().modify_stats_inner(stats)
        stats = stats.copy(speed=new_speed, senses=new_senses)
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        tunnel_width = 10 if stats.size >= Size.Huge else 5

        feature = Feature(
            name="Burrower",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can burrow through solid rock at half its burrow speed and leaves a {tunnel_width} foot wide diameter tunnel in its wake.",
        )

        return [feature]


class _Climber(EarthPower):
    def __init__(self):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return (
                not (c.speed.fly or 0)
                and not (c.speed.swim or 0)
                and not (c.speed.climb or 0)
            )

        super().__init__(
            name="Climber",
            source="SRD5.1 Giant Spider",
            icon="mountain-climbing",
            power_level=RIBBON_POWER,
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Ambusher],
            require_callback=not_already_special_movement,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        ## Spider Climb
        if stats.creature_type in {
            CreatureType.Beast,
            CreatureType.Monstrosity,
            CreatureType.Ooze,
        }:
            feature = Feature(
                name="Spider Climb",
                action=ActionType.Feature,
                description=f"{stats.selfref.capitalize()} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check",
            )
        else:
            feature = Feature(
                name="Climber",
                action=ActionType.Feature,
                hidden=True,
                description=f"{stats.selfref.capitalize()} gains a climb speed equal to its walk speed",
            )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Athletics, Skills.Acrobatics
        )
        stats = stats.copy(speed=new_speed, attributes=new_attrs)
        return stats


Burrower: Power = _Burrower()
Climber: Power = _Climber()

EarthyPowers: List[Power] = [Burrower, Climber]
