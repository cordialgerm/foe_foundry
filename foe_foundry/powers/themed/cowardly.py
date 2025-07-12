from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import Condition
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


def could_be_cowardly(stats: BaseStatblock) -> bool:
    if stats.creature_type != CreatureType.Humanoid:
        return False

    if (
        MonsterRole.Soldier in stats.additional_roles
        or MonsterRole.Bruiser in stats.additional_roles
    ):
        return False

    int_score = stats.attributes.INT < 10
    wis_score = stats.attributes.WIS < 10
    cha_score = stats.attributes.CHA < 10

    score = int_score + wis_score + cha_score
    return score >= 2 and stats.cr <= 1


class CowardlyPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Goblin",
        create_date: datetime | None = datetime(2025, 3, 22),
        power_types: List[PowerType] | None = None,
        **score_args,
    ):
        standard_score_args = (
            dict(
                require_callback=could_be_cowardly,
                require_types=CreatureType.Humanoid,
                bonus_roles=MonsterRole.Skirmisher,
            )
            | score_args
        )

        super().__init__(
            name=name,
            source=source,
            power_category=PowerCategory.Theme,
            power_level=power_level,
            theme="cowardly",
            icon=icon,
            reference_statblock=reference_statblock,
            create_date=create_date,
            score_args=standard_score_args,
            power_types=power_types,
        )


class _ScurryAndScatter(CowardlyPower):
    def __init__(self):
        super().__init__(
            name="Scurry and Scatter",
            source="Foe Foundry",
            icon="misdirection",
            power_level=LOW_POWER,
            power_types=[PowerType.Movement],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return [
            Feature(
                name="Scurry and Scatter",
                action=ActionType.Feature,
                description=f"When {stats.selfref} is hit by an attack or fails a save, all other {stats.selfref} within 20 feet may use their reaction to move up to half their movement speed without provoking opportunity attacks.",
            )
        ]


class _GrovelAndBeg(CowardlyPower):
    def __init__(self):
        super().__init__(
            name="Grovel and Beg",
            source="Foe Foundry",
            icon="kneeling",
            power_level=LOW_POWER,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        prone = Condition.Prone
        charm = Condition.Charmed
        bloodied = Condition.Bloodied
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Grovel and Beg",
            action=ActionType.Reaction,
            uses=1,
            description=f"If {stats.selfref} is {bloodied.caption} and becomes the target of a spell, ability, or attack, then it falls {prone.caption} and begs pitifully. \
                If the source of the attack, spell, or ability is within 30 feet, it must make a DC {dc} Wisdom saving throw. On a failure, it must change the target of the spell, ability, or attac. \
                This counts as a {charm.caption} effect.",
        )

        return [feature]


class _FeignDeath(CowardlyPower):
    def __init__(self):
        super().__init__(
            name="Feign Death",
            source="Foe Foundry",
            icon="dead-head",
            power_level=LOW_POWER,
            power_types=[PowerType.Stealth],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        study = action_ref("Study")
        prone = Condition.Prone
        feature = Feature(
            name="Feign Death",
            action=ActionType.Feature,
            description=f"When {stats.selfref} takes damage that reduces it to below half health, it can choose to feign its own death. \
                It falls {prone.caption} and appears as if it were dead. A creature must perform a {study} action to determine that the creature is not dead. \
                If {stats.selfref} attacks a creature that is unaware that it is still alive, it has advantage on the attack.",
        )

        return [feature]


ScurryAndScatter: Power = _ScurryAndScatter()
GrovelAndBeg: Power = _GrovelAndBeg()
FeignDeath: Power = _FeignDeath()

CowardlyPowers: list[Power] = [
    ScurryAndScatter,
    GrovelAndBeg,
    FeignDeath,
]
