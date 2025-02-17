from datetime import datetime
from typing import List

from ...attributes import Stats
from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


def score_could_be_organized(stats: BaseStatblock, requires_intelligence: bool) -> bool:
    creature_types = {c for c in CreatureType if c.could_be_organized}
    if not requires_intelligence:
        creature_types |= {CreatureType.Beast, CreatureType.Monstrosity}
    return stats.creature_type in creature_types


class OrganizedPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            power_level=power_level,
            theme="organized",
            create_date=create_date,
            score_args=dict(
                bonus_types={c for c in CreatureType if c.could_be_organized},
                require_stats=Stats.INT,
                require_roles=MonsterRole.Leader,
            )
            | score_args,
        )


class _FanaticFollowers(OrganizedPower):
    def __init__(self):
        super().__init__(
            name="Fanatic Followers",
            source="A5E SRD Crime Boss",
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(stats.cr, min_val=5)
        feature = Feature(
            name="Fanatic Followers",
            action=ActionType.Reaction,
            description=f"Whenever {stats.selfref} would be hit by an attack, they command an ally within 5 feet to use its reaction to switch places with {stats.selfref}. \
                The ally is hit by the attack instead of the boss. If the ally is killed by this attack, then all allies of {stats.selfref} gains {temphp} temporary hp.",
        )
        return [feature]


class _InspiringCommander(OrganizedPower):
    def __init__(self):
        super().__init__(
            name="Inspiring Commander", source="A5E SRD Knight", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Inspiring Commander",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} inspires other creatures of its choice within 30 feet that can hear and understand it. \
                For the next minute, inspired creatures gain a +{stats.attributes.proficiency} bonus to attack rolls and saving throws.",
        )
        return [feature]


FanaticFollowers: Power = _FanaticFollowers()
InspiringCommander: Power = _InspiringCommander()

OrganizedPowers: List[Power] = [FanaticFollowers, InspiringCommander]
