from datetime import datetime
from typing import List

from foe_foundry.damage import Condition
from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import RIBBON_POWER, Power, PowerType, PowerWithStandardScoring


class HalflingPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        power_level: float = RIBBON_POWER,
        **score_args,
    ):
        def is_halfling(stats: BaseStatblock) -> bool:
            return (
                stats.creature_subtype is not None
                and stats.creature_subtype.lower() == "halfling"
            )

        standard_score_args = dict(
            require_types=CreatureType.Humanoid,
            require_callback=is_halfling,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Species,
            power_level=power_level,
            source=source,
            create_date=create_date,
            icon=icon,
            theme="Halfling",
            reference_statblock="Spy",
            score_args=standard_score_args,
        )


# Halfling Power Brainstorm
#
# Halfling Power: Lucky
# Halfling Power: Fearless
# Halfling Power: Nimble Escape


class _HalflingLuck(HalflingPower):
    def __init__(self):
        super().__init__(
            name="Halfling Luck",
            source="Foe Foundry",
            icon="clover",
            bonus_roles=[
                MonsterRole.Ambusher,
                MonsterRole.Support,
                MonsterRole.Artillery,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Halfling Luck",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} rolls a 1 on a d20 test, it may reroll the die and must use the new roll",
        )
        return [feature]


class _HalflingBravery(HalflingPower):
    def __init__(self):
        super().__init__(
            name="Halfling Bravery",
            source="Foe Foundry",
            icon="achievement",
            bonus_roles=[
                MonsterRole.Soldier,
                MonsterRole.Defender,
                MonsterRole.Leader,
                MonsterRole.Bruiser,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(2 * stats.attributes.proficiency, min_val=5)

        feature = Feature(
            name="Halfling Bravery",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} ends all Charmed and Frightened conditions on itself and gains {temp_hp} temporary hit points.",
        )
        return [feature]


class _HalflingNimbleness(HalflingPower):
    def __init__(self):
        super().__init__(
            name="Halfling Nimbleness",
            source="Foe Foundry",
            icon="tightrope",
            bonus_roles=[MonsterRole.Ambusher, MonsterRole.Skirmisher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        disengage = action_ref("Disengage")
        grappled = Condition.Grappled.caption
        restrained = Condition.Restrained.caption
        feature = Feature(
            name="Halfling Nimbleness",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} uses {disengage} and ends any {grappled} or {restrained} conditions on itself.",
        )
        return [feature]


HalflingLuck: Power = _HalflingLuck()
HalflingBravery: Power = _HalflingBravery()
HalflingNimbleness: Power = _HalflingNimbleness()

HalflingPowers: list[Power] = [
    HalflingLuck,
    HalflingBravery,
    HalflingNimbleness,
]
