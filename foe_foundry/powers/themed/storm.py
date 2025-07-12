from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType, Shocked
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class StormPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="storm",
            icon=icon,
            reference_statblock="Storm Giant",
            power_level=power_level,
            power_type=PowerType.Theme,
            create_date=create_date,
            score_args=dict(
                require_types={
                    CreatureType.Elemental,
                    CreatureType.Giant,
                    CreatureType.Dragon,
                    CreatureType.Humanoid,
                },
                require_damage={DamageType.Lightning, DamageType.Thunder},
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type != DamageType.Lightning:
            stats = stats.copy(secondary_damage_type=DamageType.Lightning)

        return stats


class _TempestSurge(StormPower):
    def __init__(self):
        super().__init__(
            name="Tempest Surge",
            source="Foe Foundry",
            icon="lightning-storm",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=2.5, force_die=Die.d10)
        shocked = Shocked()
        dc = stats.difficulty_class

        feature = Feature(
            name="Tempest Surge",
            action=ActionType.Action,
            replaces_multiattack=3,
            recharge=5,
            description=f"{stats.selfref.capitalize()} sends out arcs of lightning at a creature it can see within 60 feet. \
                The creature must make a DC {dc} Dexterity saving throw. On a failure, the target takes {dmg.description} lightning damage \
                and is {shocked.caption} for 1 minute (save ends at end of turn). On a success, the creature takes half damage instead. {shocked.description_3rd}",
        )
        return [feature]


class _StormcallersFury(StormPower):
    def __init__(self):
        super().__init__(
            name="Stormcaller's Fury",
            icon="lightning-dissipation",
            source="SRD5.1 Call Lightning",
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = stats.target_value(target=1.5, force_die=Die.d10)

        feature = Feature(
            name="Stormcaller's Fury",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} calls down lightning on a point it can see within 120 feet. \
                Each creature within 5 feet of the point must make a DC {dc} Dexterity saving throw, taking {dmg.description} \
                lightning damage on a failure and half damage on a success. If stormy conditions are present then this save is made with disadvantage.",
        )

        return [feature]


TempestSurge: Power = _TempestSurge()
StormcallersFury: Power = _StormcallersFury()

StormPowers: List[Power] = [StormcallersFury, TempestSurge]
