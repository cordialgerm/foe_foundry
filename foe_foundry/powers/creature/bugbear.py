from datetime import datetime

from ...creature_types import CreatureType
from ...damage import Condition
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_bugbear(s: BaseStatblock) -> bool:
    return s.creature_class == "Bugbear"


class BugbearPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        power_level: float = MEDIUM_POWER,
        icon: str | None = None,
        create_date: datetime | None = datetime(2025, 4, 6),
        **score_args,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="bugbear",
            reference_statblock="Bugbear",
            power_level=power_level,
            icon=icon,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_bugbear,
                require_types=[CreatureType.Humanoid],
            )
            | score_args,
        )


class _SnatchAndGrab(BugbearPower):
    def __init__(self):
        super().__init__(
            name="Vice-Like Grip",
            icon="grab",
        )

    def generate_features(self, stats: BaseStatblock) -> list[Feature]:
        grappled = Condition.Grappled.caption
        feature = Feature(
            name="Vice-Like Grip",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack rolls against any creature it has {grappled}.",
        )

        return [feature]


class _FreakishlySkinny(BugbearPower):
    def __init__(self):
        super().__init__(
            name="Freakishly Skinny", icon="dungeon-gate", power_level=RIBBON_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> list[Feature]:
        feature = Feature(
            name="Freakishly Skinny",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can move, hide, and squeeze as though it were a Small creature.",
        )

        return [feature]


class _SurpriseSnatch(BugbearPower):
    def __init__(self):
        super().__init__(
            name="Surprise Snatch",
            icon="surprised",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> list[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.4)
        grappled = Condition.Grappled.caption
        feature = Feature(
            name="Surprise Snatch",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} attempts to drag away a creature that is unaware of it within 10 feet. \
                The target must make a DC {dc} Strength saving throw. \
                On a failure, the target takes {dmg.description} bludgeoning damage and is {grappled}. \
                {stats.selfref.capitalize()} can then drag the target up to half its speed. \
                Additionally, other creatures that were unaware of {stats.selfref} remain unaware of it.",
        )

        return [feature]


class _SurpriseStrangle(BugbearPower):
    def __init__(self):
        super().__init__(
            name="Surprise Strangle",
            icon="slipknot",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> list[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.25)
        grappled = Condition.Grappled.caption
        feature = Feature(
            name="Surprise Strangle",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting a creature, or if it has {grappled} a creature, {stats.selfref} attempts to strangle that creature. \
                The target must make a DC {dc} Strength saving throw. On a failure, the target is {grappled}, takes {dmg.description} bludgeoning damage, and cannot speak or cast spells with verbal components until the end of its next turn.",
        )

        return [feature]


class _Skulk(BugbearPower):
    def __init__(self):
        super().__init__(
            name="Skulk",
            icon="hidden",
            power_level=RIBBON_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> list[Feature]:
        feature = Feature(
            name="Skulk",
            action=ActionType.Feature,
            description=f"If {stats.selfref} misses an attack, it doesn't reveal its position to other creatures and can remain hidden.",
        )

        return [feature]


SnatchAndGrab: Power = _SnatchAndGrab()
FreakishlySkinny: Power = _FreakishlySkinny()
SurpriseSnatch: Power = _SurpriseSnatch()
Strangle: Power = _SurpriseStrangle()
Skulk: Power = _Skulk()
BugbearPowers: list[Power] = [
    SnatchAndGrab,
    FreakishlySkinny,
    SurpriseSnatch,
    Strangle,
    Skulk,
]
