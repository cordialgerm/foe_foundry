from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class HydraPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        def require_callback(s: BaseStatblock) -> bool:
            return s.creature_subtype == "Hydra"

        super().__init__(
            name=name,
            source=source,
            theme="hydra",
            reference_statblock="Hydra",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=require_callback,
                bonus_types=CreatureType.Monstrosity,
                bonus_damage=DamageType.Acid,
            )
            | score_args,
        )


class _HydraHeads(HydraPower):
    def __init__(self):
        super().__init__(
            name="Hydra Heads",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            create_date=datetime(2025, 3, 12),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Multi-Headed",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has five heads. It can make as many Opportunity Attacks as it has heads.",
        )

        feature2 = Feature(
            name="Regrowth",
            action=ActionType.Feature,
            description=f"At the start of its turn, if {stats.selfref}'s Severed Head reaction triggered last turn, it heals 20 hitpoints. If it healed, it generates two new heads.",
        )

        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.3, force_die=Die.d4)
        feature3 = Feature(
            name="Severed Head",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} takes 20 or more damage from an attack, one of its heads is severed. \
                Each other creature in a 20 foot emanation must make a DC {dc} Dexterity saving throw, taking {dmg.description} acid damage on a failed save. \
                {stats.selfref.capitalize()} may use its Regrowth ability at the start of its next turn",
        )

        return [feature1, feature2, feature3]


HydraHeads: Power = _HydraHeads()

HydraPowers: list[Power] = [HydraHeads]
