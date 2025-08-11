from foe_foundry.references import spell_ref

from ...creature_types import CreatureType
from ...damage import Condition, conditions
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


def is_frost_giant(c: BaseStatblock) -> bool:
    return c.creature_class == "Frost Giant"


class FrostGiantPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        power_types: list[PowerType] | None = None,
    ):
        super().__init__(
            name=name,
            power_category=PowerCategory.Creature,
            power_level=power_level,
            source="Foe Foundry",
            icon=icon,
            theme="frost_giant",
            reference_statblock="Frost Giant",
            power_types=power_types or [],
            score_args=dict(
                require_callback=is_frost_giant,
                require_types=CreatureType.Giant,
            ),
        )


class _AvalancheCharge(FrostGiantPower):
    def __init__(self):
        super().__init__(
            name="Avalanche Charge",
            icon="summits",
            power_types=[PowerType.Movement, PowerType.Environmental],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> list[Feature]:
        dc = stats.difficulty_class
        prone = Condition.Prone.caption
        feature = Feature(
            name="Avalanche Charge",
            action=ActionType.BonusAction,
            uses=1,
            description=(
                f"{stats.selfref.capitalize()} charges up to its speed in a straight line. Each creature in its path must make a DC {dc} Strength saving throw or be knocked {prone}. "
                f"If the terrain is snowy or icy, creatures have disadvantage on the save and do not get attacks of opportunity against {stats.selfref}."
            ),
        )
        return [feature]


class _WintersShroud(FrostGiantPower):
    def __init__(self):
        super().__init__(
            name="Winter's Shroud",
            icon="person-in-blizzard",
            power_types=[
                PowerType.Attack,
                PowerType.AreaOfEffect,
                PowerType.Environmental,
            ],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> list[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.6)
        fog_cloud = spell_ref("Fog Cloud")
        feature = Feature(
            name="Winter's Shroud",
            action=ActionType.Action,
            recharge=5,
            description=(
                f"{stats.selfref.capitalize()} exhales freezing fog in a 30-foot cone. Each creature in the area must make a DC {dc} Constitution saving throw or take {dmg.description} cold damage. The area becomes heavily obscured, as under the effects of a {fog_cloud} spell, though {stats.selfref} can see through this fog as if it were clear."
            ),
        )
        return [feature]


class _ChillingChallenge(FrostGiantPower):
    def __init__(self):
        super().__init__(
            name="Chilling Challenge",
            icon="face-to-face",
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> list[Feature]:
        dc = stats.difficulty_class
        frozen = conditions.Frozen(dc=dc)
        feature = Feature(
            name="Chilling Challenge",
            action=ActionType.BonusAction,
            uses=3,
            description=(
                f"{stats.selfref.capitalize()} challenges a creature it can see within 15 feet to a one on one duel. If the target does not attack {stats.selfref} in melee by the end of its next turn, it must make a DC {dc} Wisdom save or become {frozen.caption}. {frozen.description_3rd}"
            ),
        )
        return [feature]


AvalancheCharge: Power = _AvalancheCharge()
WintersShroud: Power = _WintersShroud()
ChillingChallenge: Power = _ChillingChallenge()

FrostGiantPowers: list[Power] = [AvalancheCharge, WintersShroud, ChillingChallenge]
