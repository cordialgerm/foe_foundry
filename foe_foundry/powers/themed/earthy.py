from datetime import datetime
from typing import List

from ...attributes import Skills
from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, RIBBON_POWER, Power, PowerType, PowerWithStandardScoring


class EarthPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return not (c.speed.fly or 0) and not (c.speed.swim or 0)

        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=power_level,
            power_type=PowerType.Theme,
            theme="earth",
            score_args=dict(
                require_types=[CreatureType.Beast, CreatureType.Monstrosity, CreatureType.Ooze],
                require_callback=not_already_special_movement,
                **score_args,
            ),
        )


class _Burrower(EarthPower):
    def __init__(self):
        super().__init__(name="Burrower", source="SRD5.1 Purple Worm", power_level=RIBBON_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        new_speed = stats.speed.copy(burrow=stats.speed.walk)
        new_senses = stats.senses.copy(blindsight=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)

        tunnel_width = 10 if stats.size >= Size.Huge else 5

        feature = Feature(
            name="Burrower",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can burrow through solid rock at half its burrow speed and leaves a {tunnel_width} foot wide diameter tunnel in its wake.",
        )

        return [feature]


class _Climber(EarthPower):
    def __init__(self):
        super().__init__(
            name="Climber",
            source="SRD5.1 Giant Spider",
            power_level=RIBBON_POWER,
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Ambusher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
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

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Athletics, Skills.Acrobatics
        )
        stats = stats.copy(speed=new_speed, attributes=new_attrs)
        return stats


Burrower: Power = _Burrower()
Climber: Power = _Climber()

EarthyPowers: List[Power] = [Burrower, Climber]
