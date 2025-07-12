from datetime import datetime
from typing import List

from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import conditions
from ...features import ActionType, Feature
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class ShamanicPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 3, 31),
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_category=PowerCategory.Theme,
            power_level=power_level,
            icon=icon,
            theme="shamanic",
            reference_statblock="Druid",
            create_date=create_date,
            score_args=dict(
                require_types=CreatureType.Humanoid,
                require_spellcasting=CasterType.Primal,
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        stats = stats.grant_spellcasting(CasterType.Primal)
        return stats


class _SpiritWalk(ShamanicPower):
    def __init__(self):
        super().__init__(
            name="Spirit Walk",
            source="Foe Foundry",
            icon="ifrit",
            power_level=HIGH_POWER,
            require_cr=5,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.hp.average * 0.25, min_val=5, max_val=100)
        invisible = conditions.Condition.Invisible.caption
        feature = Feature(
            name="Spirit Walk",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} becomes {invisible} until the end of its next turn. \
                While invisible, it can see hidden and {invisible} creatures. \
                It also gains {hp} temporary hit points.",
        )

        return [feature]


class _CommuneWithTheAncestors(ShamanicPower):
    def __init__(self):
        super().__init__(
            name="Commune with the Ancestors",
            source="Foe Foundry",
            icon="satellite-communication",
            power_level=MEDIUM_POWER,
            require_cr=5,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Commune with the Ancestors",
            action=ActionType.Reaction,
            uses=1,
            description=f"When another creature within 30 feet makes a d20 test, {stats.selfref.capitalize()} can add or subtract 5 from that roll.",
        )

        return [feature]


class _CommuneWithLand(ShamanicPower):
    def __init__(self):
        super().__init__(
            name="Commune with Land",
            source="Foe Foundry",
            icon="fuji",
            power_level=HIGH_POWER,
            require_cr=5,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.8)
        prone = conditions.Condition.Prone.caption
        feature = Feature(
            name="Commune with Land",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} communes with the land, causing earth spirits to arise in a 30 foot emanation around it. \
                Hostile creatures in that area must make a DC {dc} Strength saving throw. \
                On a failure, they take {dmg.description} bludgeoning damage and are knocked {prone}. \
                On a success, they take half damage instead"
            "",
        )
        return [feature]


class _CommuneWithAir(ShamanicPower):
    def __init__(self):
        super().__init__(
            name="Commune with Air",
            source="Foe Foundry",
            icon="windy-stripes",
            power_level=HIGH_POWER,
            require_cr=5,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.8)
        feature = Feature(
            name="Commune with Air",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} communes with the air, causing air spirits to arise in a 30 foot emanation around it. \
                Hostile creatures in that area must make a DC {dc} Strength saving throw. \
                On a failure, they take {dmg.description} thunder damage and are pushed up to 30 feet away. \
                On a success, they take half damage instead",
        )
        return [feature]


CommuneWithTheAncestors: Power = _CommuneWithTheAncestors()
CommuneWithLand: Power = _CommuneWithLand()
CommuneWithAir: Power = _CommuneWithAir()
SpiritWalk: Power = _SpiritWalk()

ShamanicPowers: list[Power] = [
    CommuneWithTheAncestors,
    CommuneWithLand,
    CommuneWithAir,
    SpiritWalk,
]
