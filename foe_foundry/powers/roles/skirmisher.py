from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType, Condition
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring
from .shared import CunningAction as _CunningAction
from .shared import NimbleEscape as _NimbleEscape


class SkirmisherPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        requires_tactics: bool = True,
        **score_args,
    ):
        def ideal_skirmisher(c: BaseStatblock) -> bool:
            # skirmishing units were typically made up of poor, lightly-armored soldiers
            return c.creature_type in {CreatureType.Humanoid} and c.cr <= 2

        def is_organized(c: BaseStatblock) -> bool:
            return c.creature_type.could_be_organized

        standard_score_args = (
            dict(
                require_roles=MonsterRole.Skirmisher,
                bonus_stats=Stats.DEX,
                bonus_skills=Skills.Acrobatics,
                bonus_speed=40,
                bonus_callback=ideal_skirmisher,
                require_callback=is_organized if requires_tactics else None,
            )
            | score_args
        )
        super().__init__(
            name=name,
            power_type=PowerType.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            icon=icon,
            theme="Skirmisher",
            reference_statblock="Goblin",
            score_args=standard_score_args,
        )


class _Skirmish(SkirmisherPower):
    def __init__(self):
        super().__init__(
            name="Skirmish",
            source="Foe Foundry",
            icon="fishing-net",
            requires_tactics=True,
            require_types=CreatureType.Humanoid,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        net_size = 10 if stats.cr <= 4 else 15
        net_range = 60 if stats.size >= Size.Large else 30
        grappled = Condition.Grappled
        restrained = Condition.Restrained

        feature = Feature(
            name="Skirmisher Nets",
            uses=1,
            replaces_multiattack=1,
            action=ActionType.Action,
            description=f"{stats.roleref.capitalize()} throws a net in a {net_size} ft. cube at a point it can see within {net_range} ft. \
                Each creature within the cube must succeed on a DC {dc} Strength save or be {grappled.caption} (escape DC {dc}) and {restrained.caption} while grappled in this way.",
        )
        return [feature]


class _HarrassingRetreat(SkirmisherPower):
    def __init__(self):
        super().__init__(
            name="Harassing Retreat",
            source="Foe Foundry",
            icon="arrowed",
            requires_tactics=True,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        range = (
            10 if len(stats.attack_types.intersection(AttackType.AllRanged())) else 5
        )

        feature = Feature(
            name="Harassing Retreat",
            action=ActionType.Reaction,
            recharge=5,
            description=f"When a hostile creature ends movement within {range} feet of {stats.roleref}, it may move up to half its movement. \
                 As part of this reaction, it may make an attack against the triggering creature.",
        )
        return [feature]


class _Speedy(SkirmisherPower):
    def __init__(self):
        super().__init__(
            name="Speedy",
            source="Foe Foundry",
            icon="fast-forward",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Speedy",
            action=ActionType.Feature,
            hidden=True,
            description=f"{stats.selfref.capitalize()}'s movement increases by 10ft and it gains proficiency in Acrobatics and Dexterity saves",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_proficiency_or_expertise(
            Skills.Acrobatics
        ).grant_save_proficiency(Stats.DEX)
        stats = stats.copy(speed=stats.speed.delta(10))
        return stats


CunningAction: Power = _CunningAction(MonsterRole.Skirmisher)
NimbleEscape: Power = _NimbleEscape(MonsterRole.Skirmisher)
HarassingRetreat: Power = _HarrassingRetreat()
Skirmish: Power = _Skirmish()
Speedy: Power = _Speedy()


SkirmisherPowers: List[Power] = [
    CunningAction,
    NimbleEscape,
    HarassingRetreat,
    Skirmish,
    Speedy,
]
