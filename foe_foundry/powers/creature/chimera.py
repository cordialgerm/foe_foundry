from datetime import datetime
from typing import List

from foe_foundry.references import feature_ref

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)
from ..themed.breath import breath


def is_chimera(s: BaseStatblock) -> bool:
    return s.creature_subtype == "Chimera"


class ChimeraPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="chimera",
            reference_statblock="Chimera",
            power_level=power_level,
            icon=icon,
            power_type=PowerCategory.Creature,
            create_date=datetime(2025, 4, 16),
            score_args=dict(
                require_callback=is_chimera,
                require_flying=True,
                bonus_types=CreatureType.Monstrosity,
            ),
        )


class _DragonsBreath(ChimeraPower):
    def __init__(self):
        super().__init__(name="Dragon's Breath", icon="dragon-breath")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = breath(
            name="Dragon's Breath",
            damage_type=DamageType.Fire,
            stats=stats,
            save="Dexterity",
            damage_multiplier=0.9,
            recharge=6,
        )

        return [feature]


class _QuarellingHeads(ChimeraPower):
    def __init__(self):
        super().__init__(name="Quarrelling Heads", icon="hydra")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        prone = Condition.Prone.caption
        dragons_breath = feature_ref("Dragon's Breath")

        feature = Feature(
            name="Quarrelling Heads",
            action=ActionType.BonusAction,
            description=f"The three heads of {stats.selfref} quarrel incessantly. Roll a d6 to determine which head is in control: \
                <ul> \
                    <li>1-2: <b>Lion</b>: {stats.selfref.capitalize()} has advantage on attack rolls against any creature with a higher AC than it.</li> \
                    <li>3-4: <b>Goat</b>: When {stats.selfref} hits with an attack, the target is knocked {prone}.</li> \
                    <li>5-6: <b>Dragon</b>: {stats.selfref.capitalize()}'s attacks deal an additional 1d6 fire damage. If all attacks hit, the {dragons_breath} ability recharges.</li> \
                </ul>",
        )

        return [feature]


DragonsBreath: Power = _DragonsBreath()
QuarellingHeads: Power = _QuarellingHeads()

ChimeraPowers: list[Power] = [
    DragonsBreath,
    QuarellingHeads,
]
