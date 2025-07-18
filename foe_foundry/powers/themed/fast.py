from datetime import datetime
from typing import List

from ...attributes import AbilityScore, Skills
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerType,
    PowerWithStandardScoring,
)


class FastPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        reference_statblock: str = "Goblin",
        power_level: float = MEDIUM_POWER,
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=power_level,
            power_category=PowerCategory.Theme,
            icon=icon,
            reference_statblock=reference_statblock,
            theme="fast",
            power_types=power_types or [PowerType.Movement],
            score_args=dict(
                require_stats=AbilityScore.DEX,
                stat_threshold=16,
                require_roles=[MonsterRole.Ambusher, MonsterRole.Skirmisher],
            )
            | score_args,
        )


class _Evasion(FastPower):
    def __init__(self):
        super().__init__(
            name="Evasion",
            icon="dodging",
            source="SRD5.1 Assassin",
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Evasion",
            action=ActionType.Feature,
            description=f"If {stats.roleref} is subjected to an effect that allows it to make a Dexterity saving throw \
            to take only half damage, {stats.roleref} instead takes no damage if it succeeds and half damage if it fails.",
        )
        return [feature]


class _NimbleReaction(FastPower):
    def __init__(self):
        super().__init__(
            name="Nimble Reaction",
            source="Foe Foundry",
            icon="running-ninja",
            bonus_speed=40,
            bonus_skills=[Skills.Acrobatics, Skills.Athletics],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Nimble Reaction",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} is the only target of a melee attack, they can move up to half their speed without provoking opportunity attacks.\
                If this movement leaves {stats.selfref} outside the attacking creature's reach, then the attack misses.",
            recharge=4,
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Acrobatics)
        stats = stats.copy(attributes=new_attrs)
        return stats


Evasion: Power = _Evasion()
NimbleReaction: Power = _NimbleReaction()

FastPowers: List[Power] = [Evasion, NimbleReaction]
