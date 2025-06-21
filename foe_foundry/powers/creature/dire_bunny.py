from datetime import datetime
from typing import List

from foe_foundry.features import ActionType, Feature
from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import Condition
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_dire_bunny(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Bunny"


class _DireBunnyPower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = MEDIUM_POWER, **score_args):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="dire_bunny",
            icon="rabbit",
            reference_statblock="Dire Bunny",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 4, 5),
            score_args=dict(
                require_callback=is_dire_bunny,
                require_types=CreatureType.Monstrosity,
            )
            | score_args,
        )


class _ThumpOfDread(_DireBunnyPower):
    def __init__(self):
        super().__init__(name="Thump of Dread", power_level=MEDIUM_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.8)
        dc = stats.difficulty_class

        feature = Feature(
            name="Thump of Dread",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} slams its massive hind legs into the ground, causing a thunderous shockwave. \
                Each creature within 10 feet must make a DC {dc} Constitution saving throw. \
                On a failed save, the target takes {dmg.description} thunder damage and is knocked {Condition.Prone.caption}. \
                On a successful save, the target takes half as much damage and isn't knocked prone.",
        )
        return [feature]


class _BurrowingDisguise(_DireBunnyPower):
    def __init__(self):
        super().__init__(name="Burrowing Disguise", power_level=MEDIUM_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hide = action_ref("Hide")
        feature = Feature(
            name="Burrowing Disguise",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} burrows into the earth and uses {hide}",
        )
        return [feature]


class _CursedCuteness(_DireBunnyPower):
    def __init__(self):
        super().__init__(name="Cursed Cuteness", power_level=MEDIUM_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Cursed Cuteness",
            action=ActionType.Feature,
            description=f"The first time another creature attempts to target {stats.selfref} with an attack, ability, or spell, it must make a DC {dc} Wisdom save. \
                On a failed save, the creature must choose a different target or lose the attack, ability, or spell. This effect counts as a Charm effect",
        )
        return [feature]


ThumpOfDread: Power = _ThumpOfDread()
BurrowingDisguise: Power = _BurrowingDisguise()
CursedCuteness: Power = _CursedCuteness()

DireBunnyPowers = [
    ThumpOfDread,
    BurrowingDisguise,
    CursedCuteness,
]
