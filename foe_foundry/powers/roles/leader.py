from datetime import datetime
from math import ceil
from typing import List

from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ...utils.rounding import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class LeaderPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Leader,
            bonus_skills=[Skills.Persuasion, Skills.Intimidation, Skills.Insight],
            bonus_stats=[Stats.CHA, Stats.INT, Stats.WIS],
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Leader",
            score_args=standard_score_args,
        )


class _CommandTheAttack(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Command the Attack",
            source="A5E SRD Knight Captain",
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Command the Attack",
            description=f"{stats.roleref.capitalize()} issues a command to all nonhostile creatures within 30 feet. \
                          Creatures who can see or hear {stats.roleref} can use their reaction to make a single weapon attack with advantage.",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
        )
        return [feature]


class _Encouragement(LeaderPower):
    def __init__(self):
        super().__init__(name="Encouragement", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(
            int(stats.attributes.stat_mod(Stats.WIS) + max(5, ceil(stats.cr * 2)))
        )

        feature = Feature(
            name="Encouragement",
            description=f"{stats.roleref.capitalize()} encourages another creature within 60 feet. \
                The chosen creature gains {hp} temporary hitpoints and may repeat a saving throw against any negative condition affecting them, ending that condition on a success.",
            action=ActionType.BonusAction,
            uses=3,
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attributes = stats.attributes.grant_proficiency_or_expertise(
            Skills.Medicine, Skills.Insight
        )
        stats = stats.copy(attributes=new_attributes)
        return stats


class _Intimidate(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Intimidate", source="Foe Foundry", require_stats=Stats.CHA
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Intimidate",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.roleref.capitalize()} chooses a target that can hear them within 60 ft. \
                The target must make a contested Insight check against {stats.roleref}'s Intimidation. \
                On a failure, the target is **Frightened** of {stats.roleref} for 1 minute (save ends at end of turn).\
                While Frightened in this way, attacks made against the target have advantage.",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _StayInFormation(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Move Out",
            source="A5E SRD Bugbear Chief",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Stay in Formation",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} issues a command to all nonhostile creatures within 30 feet. \
                Creatures who can see or hear {stats.roleref} can use their reaction to move up to half their speed without provoking opportunity attacks.",
        )
        return [feature]


CommandTheAttack: Power = _CommandTheAttack()
Encouragement: Power = _Encouragement()
Intimidate: Power = _Intimidate()
StayInFormation: Power = _StayInFormation()

LeaderPowers: List[Power] = [
    CommandTheAttack,
    Encouragement,
    Intimidate,
    StayInFormation,
]
