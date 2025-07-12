from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_ogre(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Ogre"


class OgrePower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str = "ogre",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_level=power_level,
            create_date=create_date,
            power_type=PowerType.Creature,
            icon=icon,
            theme="ogre",
            reference_statblock="Ogre",
            score_args=dict(require_callback=is_ogre, require_types=CreatureType.Giant)
            | score_args,
        )


class _Wallsmash(OgrePower):
    def __init__(self):
        super().__init__(
            name="Wallsmasha",
            source="Foe Foundry",
            icon="broken-wall",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 4, 7),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.9, force_die=Die.d10)
        dc = stats.difficulty_class
        prone = Condition.Prone.caption

        feature1 = Feature(
            name="Wallsmasha",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} deals double damage to objects and structures.",
        )
        feature2 = Feature(
            name="SMAAASH!",
            action=ActionType.Action,
            recharge=6,
            description=f"{stats.selfref.capitalize()} swings its club at a point it can see within 10 feet. Each other creature or object within 10 feet must make a DC {dc} Dexterity saving throw. \
                On a failure, creatures take {dmg.description} bludgeoning damage and are knocked {prone}. On a success, they take half damage instead. If {stats.selfref} destroys a medium-sized or larger object with this ability, it recharges this ability immediately.",
        )

        return [feature1, feature2]


class _BurnBelch(OgrePower):
    def __init__(self):
        super().__init__(
            name="Burnbelch",
            source="Foe Foundry",
            icon="gas-stove",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 4, 7),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.6, force_die=Die.d10, force_even=True)
        burning_dmg = DieFormula.from_dice(d10=(dmg.d10 or 0) // 2)
        burning = conditions.Burning(damage=burning_dmg).caption

        feature = Feature(
            name="Burnbelch",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} exhales a 15-foot cone of highly flammable volatiles. Each creature in that area must make a DC {dc} Dexterity saving throw. On a failure, a creatures takes {dmg.description} fire damage and is {burning}. On a success, a creatures takes half damage instead.",
        )

        return [feature]


class _ChainCrack(OgrePower):
    def __init__(self):
        super().__init__(
            name="Chaincrack",
            source="Foe Foundry",
            icon="andromeda-chain",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 4, 7),
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d6)
        dazed = conditions.Dazed()
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Chaincrack",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} swings its chain at up to three creatures within 30 feet. The targeted creatures must make a DC {dc} Strength saving throw. \
                On a failure, a creature takes {dmg.description} bludgeoning damage and is {dazed.caption} until the end of its next turn. On a success, a creatures takes half damage instead. {dazed.description_3rd}",
        )
        return [feature]


Wallsmash: Power = _Wallsmash()
Burnbelch: Power = _BurnBelch()
ChainCrack: Power = _ChainCrack()

OgrePowers: list[Power] = [Burnbelch, ChainCrack, Wallsmash]
