from datetime import datetime
from typing import List

from foe_foundry.references import creature_ref

from ...creature_types import CreatureType
from ...damage import conditions
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)

Madness = conditions.CustomCondition(
    name="Madness",
    caption="<span class='condition condition-madness'>Madness</span>",
    description="",
    description_3rd="",
)


def is_nothic(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Hollow Gazer"


class _NothicPower(PowerWithStandardScoring):
    def __init__(
        self, name: str, icon: str = "cursed-star", power_level: float = LOW_POWER
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="hollow_gazer",
            reference_statblock="Hollow Gazer",
            icon=icon,
            power_level=power_level,
            power_type=PowerCategory.Creature,
            create_date=datetime(2025, 4, 4),
            score_args=dict(
                require_callback=is_nothic,
                require_types=CreatureType.Aberration,
            ),
        )


class _TwistedProphecy(_NothicPower):
    def __init__(self):
        super().__init__(name="Twisted Prophecy", power_level=HIGH_POWER)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d6)
        feature = Feature(
            name="Twisted Prophecy",
            action=ActionType.Feature,
            description=f"At the start of combat, {stats.selfref} utters a twisted prophecy and chooses a number from 1 to 20. Whenever any creature, including {stats.selfref}, rolls the chosen number on a d20 test, \
                that creature suffers {dmg.description} psychic damage. {stats.selfref.capitalize()} then gains a level of {Madness.caption}",
        )

        return [feature]


class _ShatteredOmens(_NothicPower):
    def __init__(self):
        super().__init__(name="Shattered Omens", power_level=HIGH_POWER)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Mind-Warping Truths",
            action=ActionType.Reaction,
            description=f"When a creature succeeds or fails a d20 test by 5 or less, {stats.selfref.capitalize()} forces that creature to re-roll the d20 test. {stats.selfref.capitalize()} then gains a level of {Madness.caption}.",
        )

        return [feature]


class _MindShatteringPrediction(_NothicPower):
    def __init__(self):
        super().__init__(name="Mind-Shattering Prediction", power_level=HIGH_POWER)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d6)
        feature = Feature(
            name="Mind-Shattering Prediction",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} pronounces a grim prophecy about a creature it can see. If the prophecy does not come true by the end of {stats.selfref}'s next turn, then the creature takes {dmg.description} psychic damage. If the prophecy does come true, {stats.selfref} gains a level of {Madness.caption}.",
        )

        return [feature]


class _WarpingMadness(_NothicPower):
    def __init__(self):
        super().__init__(
            name="Warping Madness", icon="mad-scientist", power_level=RIBBON_POWER
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        gibbering_mouther = creature_ref("Gibbering Mouther")
        feature1 = Feature(
            name="Warping Madness",
            action=ActionType.Feature,
            description=f"If {stats.selfref} dies with 3 or more levels of {Madness.caption}, a {gibbering_mouther} immediately spawns and joins the combat, acting next in initiative.",
        )

        dmg = stats.target_value(target=0.333, force_die=Die.d6)

        feature2 = Feature(
            name="Madness Boost",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"The attack deals an additional {dmg.description} psychic damage for each level of {Madness.caption}.",
        )

        return [feature1, feature2]


TwistedProphecy: Power = _TwistedProphecy()
ShatteredOmens: Power = _ShatteredOmens()
DoomedPrediction: Power = _MindShatteringPrediction()
WarpingMadness: Power = _WarpingMadness()

NothicPowers: List[Power] = [
    TwistedProphecy,
    ShatteredOmens,
    DoomedPrediction,
    WarpingMadness,
]
