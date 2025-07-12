from datetime import datetime
from typing import List

from foe_foundry.features import ActionType, Feature

from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


def is_wight(c: BaseStatblock) -> bool:
    return c.creature_subtype == "Wight"


class WightPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str,
        source: str = "Foe Foundry",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 4, 12),
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="Wight",
            reference_statblock="Wight",
            icon=icon,
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_wight,
                require_types=[CreatureType.Undead],
                bonus_damage=DamageType.Cold,
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)

        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Cold)

        return stats


class _SoulChillingCommand(WightPower):
    def __init__(self):
        super().__init__(
            name="Soul Chilling Command",
            icon="overlord-helm",
            power_level=MEDIUM_POWER,
            require_roles=MonsterRole.Leader,
            bonus_damage=DamageType.Cold,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(
            target=2 * stats.attributes.proficiency, force_die=Die.d6
        )

        feature = Feature(
            name="Soul-Chilling Command",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} commands up to 6 friendly undead of lower CR in a soul-chilling voice. \
                Each undead may use its reaction to move up to half its speed and make an attack. \
                If the attack hits, it deals {dmg.description} additional Cold damage.",
        )

        return [feature]


class _HeartFreezingGrasp(WightPower):
    def __init__(self):
        super().__init__(
            name="Heart Freezing Grasp",
            icon="ice-spell-cast",
            power_level=MEDIUM_POWER,
            bonus_damage=DamageType.Cold,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=0.8, force_die=Die.d6)
        dc = stats.difficulty_class
        frozen = conditions.Frozen(dc=dc)
        feature = Feature(
            name="Heart Freezing Grasp",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} reaches out to grasp a target within 5 feet. The target must make a DC {dc} Constitution save. \
                On a failed save, the target takes {dmg.description} Cold damage and is {frozen.caption}. \
                {stats.selfref.capitalize()} gains temporary HP equal to the damage dealt. {frozen.description_3rd}",
        )

        return [feature]


HeartFreezingGrasp: Power = _HeartFreezingGrasp()
SoulChillingCommand: Power = _SoulChillingCommand()

WightPowers: list[Power] = [
    HeartFreezingGrasp,
    SoulChillingCommand,
]
