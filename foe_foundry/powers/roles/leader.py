from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...skills import AbilityScore, Skills
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_positive_leader(c: BaseStatblock) -> bool:
    return c.creature_type in {
        CreatureType.Humanoid,
        CreatureType.Celestial,
        CreatureType.Dragon,
        CreatureType.Elemental,
        CreatureType.Fey,
        CreatureType.Giant,
    }


class LeaderPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_roles=MonsterRole.Leader,
            bonus_skills=[Skills.Persuasion, Skills.Intimidation, Skills.Insight],
            bonus_stats=[AbilityScore.CHA, AbilityScore.INT, AbilityScore.WIS],
            **score_args,
        )
        super().__init__(
            name=name,
            power_category=PowerCategory.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Leader",
            icon=icon,
            reference_statblock="Knight",
            power_types=power_types,
            score_args=standard_score_args,
        )


class _CommandTheAttack(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Command the Attack",
            icon="spears",
            source="A5E SRD Knight Captain",
            power_level=HIGH_POWER,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Command the Attack",
            description=f"{stats.roleref.capitalize()} issues a command to all allied creatures within 30 feet. \
                          Creatures who can see or hear {stats.roleref} can use their reaction to make a single weapon attack with advantage.",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
        )
        return [feature]


class _Intimidate(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Intimidate",
            source="Foe Foundry",
            require_stats=AbilityScore.CHA,
            icon="terror",
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        frightened = Condition.Frightened
        feature = Feature(
            name="Intimidate",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.roleref.capitalize()} chooses a target that can hear them within 60 ft. \
                The target must make a contested Insight check against {stats.roleref}'s Intimidation. \
                On a failure, the target is {frightened.caption} of {stats.roleref} for 1 minute (save ends at end of turn).\
                While Frightened in this way, attacks made against the target have advantage.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _StayInFormation(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Stay In Formation",
            icon="roman-shield",
            source="A5E SRD Bugbear Chief",
            power_types=[PowerType.Utility],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Stay in Formation",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} issues a command to all allied creatures within 30 feet. \
                Creatures who can see or hear {stats.roleref} can use their reaction to move up to half their speed without provoking opportunity attacks.",
        )
        return [feature]


class _FanaticFollowers(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Fanatic Followers",
            icon="minions",
            source="A5E SRD Crime Boss",
            power_level=HIGH_POWER,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(3 + 1.5 * stats.cr, min_val=5)
        feature = Feature(
            name="Fanatic Followers",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} would be hit by an attack, they command an ally within 5 feet to use its reaction to switch places with {stats.selfref}. \
                The ally is hit by the attack instead. If the ally is killed by this attack, then {stats.selfref} gains {temphp} temporary hp.",
        )
        return [feature]


class _InspiringCommander(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Inspiring Commander",
            source="A5E SRD Knight",
            icon="caesar",
            power_level=HIGH_POWER,
            require_callback=is_positive_leader,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Inspiring Commander",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} inspires other creatures of its choice within 30 feet that can hear and understand it. \
                For the next minute, inspired creatures gain a +{stats.attributes.proficiency} bonus to attack rolls and saving throws.",
        )
        return [feature]


class _CommandTheTroops(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Command the Troops",
            source="Foe Foundry",
            icon="rank-3",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Command the Troops",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} commands a willing creature within 30 feet to use its reaction and make an attack at advantage",
        )

        return [feature]


class _RallyTheTroops(LeaderPower):
    def __init__(self):
        super().__init__(
            name="Rally the Troops",
            icon="rally-the-troops",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 2, 23),
            require_callback=is_positive_leader,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.target_value(target=0.5).average, min_val=5)

        feature = Feature(
            name="Rally the Troops",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=5,
            description=f"{stats.selfref.capitalize()} rallies all friendly creatures within 60 feet, granting them {hp} temporary hit points.",
        )

        return [feature]


CommandTheTroops: Power = _CommandTheTroops()
CommandTheAttack: Power = _CommandTheAttack()
FanaticFollowers: Power = _FanaticFollowers()
InspiringCommander: Power = _InspiringCommander()
Intimidate: Power = _Intimidate()
RallyTheTroops: Power = _RallyTheTroops()
StayInFormation: Power = _StayInFormation()

LeaderPowers: List[Power] = [
    CommandTheTroops,
    CommandTheAttack,
    FanaticFollowers,
    InspiringCommander,
    Intimidate,
    RallyTheTroops,
    StayInFormation,
]
