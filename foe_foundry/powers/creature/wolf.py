from datetime import datetime
from typing import List

from foe_foundry.features import ActionType, Feature
from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class _WolfPower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = MEDIUM_POWER, **score_args):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Wolf"

        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="wolf",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 3, 28),
            score_args=dict(
                require_callback=require_callback,
                require_types=CreatureType.Beast,
            )
            | score_args,
        )


class _SnappingJaws(_WolfPower):
    def __init__(self):
        super().__init__(name="Snapping Jaws", power_level=MEDIUM_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        grappled = Condition.Grappled.caption
        prone = Condition.Prone.caption
        dc = stats.difficulty_class
        if stats.size >= Size.Huge:
            condition = ""
        else:
            condition = f"if the target is {Size.Medium} or smaller, "

        feature = Feature(
            name="Snapping Jaws",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, {condition}the target is either {grappled} (escape DC {dc}) or {prone}",
        )
        return [feature]


class _Howl(_WolfPower):
    def __init__(self):
        super().__init__(name="Howl", power_level=MEDIUM_POWER, require_cr=1)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(number=stats.cr * 3, min_val=5, max_val=50)

        feature = Feature(
            name="Howl",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} howls, bolstering the resolve of its allies. \
                Each ally within 60 feet that hears the howl for the first time in a day gains {temphp} temporary hitpoints.",
            uses=1,
        )

        return [feature]


SnappingJaws: Power = _SnappingJaws()
Howl: Power = _Howl()


WolfPowers: list[Power] = [Howl, SnappingJaws]
