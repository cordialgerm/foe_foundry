from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_manticore(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Manticore"


class ManticorePower(PowerWithStandardScoring):
    def __init__(self, name: str, power_level: float = MEDIUM_POWER):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="manticore",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=datetime(2025, 4, 15),
            score_args=dict(
                require_callback=is_manticore,
                require_flying=True,
                bonus_types=CreatureType.Monstrosity,
            ),
        )


class _SpikeVolley(ManticorePower):
    def __init__(self):
        super().__init__(name="Spike Volley")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.75, force_die=Die.d6)
        dc = stats.difficulty_class_easy
        blinded = Condition.Blinded.caption

        feature = Feature(
            name="Spike Volley",
            action=ActionType.Action,
            recharge=4,
            description=f"{stats.selfref.capitalize()} releases a volley of razor-sharp spines from its spiked tail. Each creature in a 60-foot cone must make a DC {dc} Dexterity saving throw. \
                On a failure, a creature takes {dmg.description} piercing damage. If the creature fails by 5 or more, it is also {blinded} (save ends at end of turn). \
                On a success, the creature takes half damage instead.",
        )

        return [feature]


class _CruelJeer(ManticorePower):
    def __init__(self):
        super().__init__(name="Cruel Jeer")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Cruel Jeer",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} targets a creature that can hear it within 60 feet with a cruel jeer. The target must make a DC {dc} Wisdom save. \
                On a failure, the target has disadvantage on the next attack roll it makes before the end of its next turn.",
        )

        return [feature]


SpikeVolley: Power = _SpikeVolley()
CruelJeer: Power = _CruelJeer()

ManticorePowers: list[Power] = [
    SpikeVolley,
    CruelJeer,
]
