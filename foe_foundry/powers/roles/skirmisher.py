from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import AttackType, Condition
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class SkirmisherPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        requires_tactics: bool = True,
        reference_statblock: str = "Goblin",
        power_types: List[PowerType] | None = None,
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
            power_category=PowerCategory.Role,
            power_level=power_level,
            source=source,
            create_date=create_date,
            icon=icon,
            theme="Skirmisher",
            reference_statblock=reference_statblock,
            power_types=power_types,
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
            power_types=[PowerType.AreaOfEffect, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
            power_types=[PowerType.Attack, PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        range = (
            10 if len(stats.attack_types.intersection(AttackType.AllRanged())) else 5
        )

        if stats.cr < 1:
            recharge = None
            uses = 1
        else:
            recharge = 5
            uses = None

        feature = Feature(
            name="Harassing Retreat",
            action=ActionType.Reaction,
            recharge=recharge,
            uses=uses,
            description=f"When a hostile creature ends movement within {range} feet of {stats.roleref}, it may move up to half its movement. \
                 As part of this reaction, it may make an attack against the triggering creature.",
        )
        return [feature]


class _Speedy(SkirmisherPower):
    def __init__(self):
        super().__init__(
            name="Speedy",
            source="Foe Foundry",
            icon="fast-forward-button",
            power_level=LOW_POWER,
            power_types=[PowerType.Buff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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


class _NimbleEscape(SkirmisherPower):
    def __init__(self):
        super().__init__(
            name="Nimble Escape",
            source="SRD5.1 Goblin",
            reference_statblock="Goblin",
            icon="exit-door",
            power_types=[PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hide = action_ref("Hide")
        disengage = action_ref("Disengage")
        feature = Feature(
            name="Nimble Escape",
            action=ActionType.BonusAction,
            description=f"{stats.roleref.capitalize()} uses {disengage} or {hide}.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.copy(has_unique_movement_manipulation=True)


NimbleEscape: Power = _NimbleEscape()
HarassingRetreat: Power = _HarrassingRetreat()
Skirmish: Power = _Skirmish()
Speedy: Power = _Speedy()


SkirmisherPowers: List[Power] = [
    NimbleEscape,
    HarassingRetreat,
    Skirmish,
    Speedy,
]
