from datetime import datetime
from typing import List

from ...attack_template import natural as natural_attacks
from ...damage import Condition
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_spider(stats: BaseStatblock) -> bool:
    return stats.creature_class == "Spider" or stats.creature_subtype == "Spider"


class SpiderPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime = datetime(2025, 3, 28),
        **score_args,
    ):
        standard_score_args = dict(require_callback=is_spider) | score_args

        super().__init__(
            name=name,
            power_type=PowerCategory.CreatureType,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Spider",
            icon=icon,
            reference_statblock="Giant Spider",
            score_args=standard_score_args,
        )


class _Web(SpiderPower):
    def __init__(self):
        super().__init__(
            name="Web",
            source="SRD 5.1 Giant Spider",
            icon="spider-web",
            attack_names={
                "-",
                natural_attacks.Bite,
                natural_attacks.Claw,
                natural_attacks.Stinger,
            },
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        restrained = Condition.Restrained

        feature1 = Feature(
            name="Spider Climb",
            action=ActionType.Feature,
            description=f"{stats.selfref} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check.",
        )

        feature2 = Feature(
            name="Web Sense",
            action=ActionType.Feature,
            description=f"While in contact with a web, {stats.selfref} knows the exact location of any other creature in contact with the same web.",
        )

        feature3 = Feature(
            name="Web",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} shoots a sticky web at a point it can see within 60 feet. \
                Each creature within a 20 foot cube centered at the point must make a DC {dc} Dexterity saving throw or become {restrained.caption} (save ends at end of turn). \
                The area of the web is considered difficult terrain, and any creature that ends its turn in the area must repeat the save or become restrained.",
        )

        return [feature1, feature2, feature3]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        stats = stats.copy(speed=new_speed)
        return stats


Web: Power = _Web()
SpiderPowers: list[Power] = [Web]
