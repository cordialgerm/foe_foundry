from datetime import datetime
from typing import List

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class PoisonPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Theme,
            power_level=power_level,
            create_date=create_date,
            theme="poison",
            score_args=dict(
                require_types=[
                    CreatureType.Plant,
                    CreatureType.Aberration,
                    CreatureType.Monstrosity,
                ],
                bonus_damage=DamageType.Poison,
                attack_names=[
                    "-",
                    weapon.Daggers,
                    weapon.Shortswords,
                    weapon.RapierAndShield,
                    weapon.Crossbow,
                    weapon.HandCrossbow,
                    weapon.Longbow,
                    weapon.Shortbow,
                    natural.Bite,
                    natural.Claw,
                    natural.Spit,
                    natural.Stinger,
                    natural.Tentacle,
                    spell.Poisonbolt,
                ],
            )
            | score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
        return stats


class _PoisonousBurst(PoisonPower):
    def __init__(self):
        super().__init__(name="Poisonous Burst", source="SRD5.1 Ice Mephit")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(2 + stats.cr, force_die=Die.d6)
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 4, min_val=10, max_val=60)

        feature = Feature(
            name="Poisonous Burst",
            description=f"When {stats.selfref} dies, they release a spray of poison. Each creature within {distance} ft must succeed on a DC {dc} Constitution save or take {dmg.description} poison damage",
            action=ActionType.Reaction,
        )
        return [feature]


class _ToxicPoison(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Toxic Poison",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            create_date=datetime(2023, 11, 24),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        susceptible = conditions.Susceptible(DamageType.Poison)
        feature1 = Feature(
            name="Toxic Poison",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} forces it to make a DC {dc} Constitution saving throw. \
                On a failure, it gains {susceptible.caption} (save ends at end of turn). {susceptible.description_3rd}",
        )

        return [feature1]


PoisonousBurst: Power = _PoisonousBurst()
ToxicPoison: Power = _ToxicPoison()

PoisonPowers: List[Power] = [PoisonousBurst, ToxicPoison]
