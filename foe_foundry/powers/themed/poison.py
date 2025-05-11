from datetime import datetime
from typing import List

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
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
            reference_statblock="Hydra",
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Beast,
                    CreatureType.Plant,
                    CreatureType.Aberration,
                    CreatureType.Monstrosity,
                ],
                require_damage=DamageType.Poison,
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

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
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


class _PoisonDart(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Poison Dart",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 2),
            require_types=[CreatureType.Humanoid, CreatureType.Fey],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=1.75 if stats.multiattack > 2 else 1.1)
        dc = stats.difficulty_class
        weakened = conditions.Weakened(save_end_of_turn=False)
        poisoned = Condition.Poisoned

        feature = Feature(
            name="Poison Darts",
            description=f"{stats.selfref.capitalize()} throws poisoned darts at a target within 30 feet. The target must make a DC {dc} Dexterity save. On a failure, the target takes {dmg.description} poison damage and is {poisoned.caption} (save ends). While poisoned in this way, the target is {weakened.caption}. {weakened.description_3rd}",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
        )

        return [feature]


class _WeakeningPoison(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Weakening Poison",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 2),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        weakened = conditions.Weakened(save_end_of_turn=False)
        feature = Feature(
            name="Weakeneing Poison",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {weakened.caption} until the end of its next turn. {weakened.description_3rd}",
        )
        return [feature]


class _PoisonousBlood(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Poisonous Blood",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 14),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        poisoned = Condition.Poisoned
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Poisonous Blood",
            action=ActionType.Reaction,
            description=f"When {stats.selfref} takes piercing or bludgeoning damage, each other creature in a 10 foot radius must make a DC {dc} Constitution save or be {poisoned.caption} (save ends at end of turn).",
        )
        return [feature]


class _VenemousMiasma(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Venemous Miasma",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 14),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        poisoned = Condition.Poisoned
        dmg = int(stats.target_value(dpr_proportion=0.2).average)
        feature = Feature(
            name="Venemous Miasma",
            action=ActionType.Feature,
            description=f"Any creature that ends its turn within 10 feet of {stats.selfref} takes {dmg} poison damage. If a creature has suffered this damage at least 3 times within an hour, it becomes {poisoned.caption} for the next hour.",
        )
        return [feature]


class _VileVomit(PoisonPower):
    def __init__(self):
        super().__init__(
            name="Vile Vomit",
            source="Foe Foundry",
            create_date=datetime(2025, 3, 14),
            require_types=[CreatureType.Undead, CreatureType.Monstrosity],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        poisoned = Condition.Poisoned
        dmg = stats.target_value(dpr_proportion=1.2)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Vile Vomit",
            action=ActionType.Action,
            uses=1,
            description=f"{stats.selfref.capitalize()} vomits a vile substance in a 15 foot cone. Each creature in that area must make a DC {dc} Constitution saving throw. \
                 On a failure, the creature takes {dmg.description} Poison damage and is {poisoned.caption} (save ends at end of turn). \
                 On a success, the creature takes half damage instead.",
        )
        return [feature]


PoisonousBurst: Power = _PoisonousBurst()
ToxicPoison: Power = _ToxicPoison()
PoisonDart: Power = _PoisonDart()
PoisonousBlood: Power = _PoisonousBlood()
VenemousMiasma: Power = _VenemousMiasma()
VileVomit: Power = _VileVomit()
WeakeningPoison: Power = _WeakeningPoison()

PoisonPowers: List[Power] = [
    PoisonousBurst,
    ToxicPoison,
    PoisonDart,
    PoisonousBlood,
    VenemousMiasma,
    VileVomit,
    WeakeningPoison,
]
