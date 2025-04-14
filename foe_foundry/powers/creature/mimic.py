from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_mimic(s: BaseStatblock) -> bool:
    return s.creature_class == "Mimic"


class MimicPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 4, 13),
        **score_args,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="mimic",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_mimic,
                require_types=CreatureType.Monstrosity,
                bonus_damage=DamageType.Acid,
            )
            | score_args,
        )


class _ComfortingFamiliarity(MimicPower):
    def __init__(self):
        super().__init__(
            name="Comforting Familiarity",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Comforting Familiarity",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can telepathically detect creatures that are about to view it. \
                It takes the form of a familiar object to one or more of the approaching creatures (such as a childhood toy or old family heirloom). \
                A creature that sees the familiar object must succeed on a DC {dc} Wisdom saving throw or approach {stats.selfref}. \
                Using this ability does not reveal {stats.selfref} to the creature.",
        )

        return [feature]


class _InhabitArmor(MimicPower):
    def __init__(self):
        super().__init__(
            name="Inhabit Armor",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(0.25, force_die=Die.d4)

        grappled = conditions.Condition.Grappled.caption
        swallowed = conditions.Swallowed(
            damage=dmg,
        )
        feature = Feature(
            name="Inhabit Armor",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} infests the armor of a creature it has {grappled}. The creature is considered {swallowed}. \
                Any damage dealt to {stats.selfref} is split with the grappled creature.",
        )
        return [feature]


class _SplinterStep(MimicPower):
    def __init__(self):
        super().__init__(
            name="Splinter Step",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hide = action_ref("Hide")
        feature = Feature(
            name="Splinter Step",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} breaks apart into a swarm of tiny splinters and moves up to 20 feet without provoking opportunity attacks.\
                It then reforms into a new object and uses {hide}, making its Stealth check with advantage.",
        )

        return [feature]


class _MagneticAttraction(MimicPower):
    def __init__(self):
        super().__init__(
            name="Magnetic Attraction",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Magnetic Attraction",
            action=ActionType.Feature,
            description=f"Any creature that starts its turn within 30 feet of {stats.selfref} that is carrying metal weapons or armor \
                must make a DC {dc} Strength saving throw. On a failure, the creature is pulled up to 10 feet closer to {stats.selfref} and its speed is 0 until the end of its turn.",
        )
        return [feature]


class _HollowHome(MimicPower):
    def __init__(self):
        super().__init__(
            name="Hollow Home",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        grappled = conditions.Condition.Grappled.caption
        feature = Feature(
            name="Hollow Home",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} reshapes itself so that objects, walls, and ceilings within a 30 foot radius are now all extensions of its body. \
                 The space is difficult terrain and creatures that end their turn inside the space are {grappled} (escape DC {dc}).",
        )
        return [feature]


ComfortingFamiliarty: Power = _ComfortingFamiliarity()
InhabitArmor: Power = _InhabitArmor()
SplinterStep: Power = _SplinterStep()
MagneticAttraction: Power = _MagneticAttraction()
HollowHome: Power = _HollowHome()

MimicPowers: list[Power] = [
    ComfortingFamiliarty,
    InhabitArmor,
    SplinterStep,
    MagneticAttraction,
    HollowHome,
]
