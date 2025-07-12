from datetime import datetime
from math import ceil
from typing import List

from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


class SupportPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Support,
            bonus_skills=[Skills.Medicine, Skills.Insight],
            bonus_stats=[Stats.CHA, Stats.INT, Stats.WIS],
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerCategory.Role,
            power_level=power_level,
            source=source,
            icon=icon,
            create_date=create_date,
            theme="Support",
            reference_statblock="Priest",
            score_args=standard_score_args,
        )


class _Encouragement(SupportPower):
    def __init__(self):
        super().__init__(
            name="Encouragement",
            icon="talk",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 1),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(
            int(stats.attributes.stat_mod(Stats.WIS) + max(5, ceil(stats.cr * 2)))
        )

        feature = Feature(
            name="Encouragement",
            description=f"{stats.selfref.capitalize()} encourages another creature within 60 feet. \
                The chosen creature gains {hp} temporary hitpoints and may repeat a saving throw against any negative condition affecting them, ending that condition on a success.",
            action=ActionType.BonusAction,
            uses=3,
        )

        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attributes = stats.attributes.grant_proficiency_or_expertise(
            Skills.Medicine, Skills.Insight
        )
        stats = stats.copy(attributes=new_attributes)
        return stats


class _Guidance(SupportPower):
    def __init__(self):
        super().__init__(
            name="Guidance",
            icon="three-friends",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 1),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Guidance",
            description=f"{stats.selfref.capitalize()} grants guidance to a friendly creature within 60 feet. \
                The chosen creature may add a d4 to a failed d20 test.",
            action=ActionType.Reaction,
            uses=3,
        )
        return [feature]


class _Sanctuary(SupportPower):
    def __init__(self):
        super().__init__(
            name="Sanctuary",
            icon="church",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 1),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Sanctuary",
            description=f"Any creature that attempts to target {stats.selfref} with a harmful attack, spell, or ability must first succeed on a DC {dc} Wisdom saving throw or be unable to target {stats.selfref}.",
            action=ActionType.Feature,
        )
        return [feature]


class _WardingBond(SupportPower):
    def __init__(self):
        super().__init__(
            name="Warding Bond",
            icon="chained-heart",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 1),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        boost = max(1, stats.attributes.proficiency // 3)
        feature = Feature(
            name="Warding Bond",
            description=f"{stats.selfref.capitalize()} forms a bond with a willing creature within 30 feet. \
                Both {stats.selfref} and the target gain a +{boost} bonus to AC and resistance to all damage. \
                Whenever {stats.selfref} or target takes damage, the other takes the same amount of damage.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


Encouragement: Power = _Encouragement()
Guidance: Power = _Guidance()
Sanctuary: Power = _Sanctuary()
WardingBond: Power = _WardingBond()

SupportPowers: list[Power] = [Encouragement, Guidance, Sanctuary, WardingBond]
