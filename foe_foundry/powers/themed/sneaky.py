from datetime import datetime
from typing import List

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class SneakyPower(PowerWithStandardScoring):
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
            theme="sneaky",
            power_level=power_level,
            power_type=PowerType.Theme,
            create_date=create_date,
            score_args=dict(
                require_roles=[
                    MonsterRole.Ambusher,
                    MonsterRole.Skirmisher,
                    MonsterRole.Leader,
                ],
                require_stats=Stats.DEX,
                bonus_skills=Skills.Stealth,
                stat_threshold=14,
            )
            | score_args,
        )


class _SneakyStrike(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Sneaky Strike",
            source="FoeFoundryOriginal",
            power_level=HIGH_POWER,
            require_attack_types=AttackType.AllWeapon(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(max(1.5 * stats.cr, 2 + stats.cr), force_die=Die.d6)

        feature = Feature(
            name="Sneaky Strike",
            description=f"{stats.roleref.capitalize()} deals an additional {dmg.description} damage immediately after hitting a target if the attack was made with advantage.",
            action=ActionType.BonusAction,
        )

        return [feature]


class _FalseAppearance(SneakyPower):
    def __init__(self):
        super().__init__(
            name="False Appearance",
            source="SRD1.2 Animated Armor",
            power_level=RIBBON_POWER,
            bonus_types=[
                CreatureType.Plant,
                CreatureType.Construct,
                CreatureType.Ooze,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="False Appearance",
            action=ActionType.Feature,
            description=f"As long as {stats.selfref} remains motionless it is indistinguishable from its surrounding terrain.",
        )
        return [feature]


class _Vanish(SneakyPower):
    def __init__(self):
        super().__init__(name="Vanish", source="SRD5.1 Ranger")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Vanish",
            description=f"{stats.selfref.capitalize()} can use the Hide action as a bonus action even if only lightly obscured.",
            action=ActionType.BonusAction,
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _CheapShot(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Cheap Shot",
            source="FoeFoundryOriginal",
            require_attack_types=AttackType.AllMelee(),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        reach = stats.attack.reach or 5

        feature = Feature(
            name="Cheap Shot",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} kicks a prone creature within {reach} ft. The target must make a DC {dc} Strength \
                save or have its speed reduced to zero until the end of its next turn.",
        )
        return [feature]


class _ExploitAdvantage(SneakyPower):
    def __init__(self):
        super().__init__(
            name="Deadeye Shot",
            source="A5E SRD Deadeye Shot",
            require_attack_types=AttackType.AllRanged(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Deadeye Shot",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.selfref.capitalize()} gains advantage on the next attack it makes until end of turn.",
        )
        return [feature]


CheapShot: Power = _CheapShot()
ExploitAdvantage: Power = _ExploitAdvantage()
FalseAppearance: Power = _FalseAppearance()
SneakyStrike: Power = _SneakyStrike()
Vanish: Power = _Vanish()


SneakyPowers: List[Power] = [
    CheapShot,
    ExploitAdvantage,
    FalseAppearance,
    SneakyStrike,
    Vanish,
]
