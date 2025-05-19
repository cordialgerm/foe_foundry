from datetime import datetime
from math import ceil
from typing import List, Tuple

from numpy.random import Generator

from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Bleeding, Condition, DamageType
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...spells import conjuration
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class PlantPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Plant, **score_args)
        super().__init__(
            name=name,
            power_type=PowerType.CreatureType,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Plant",
            reference_statblock="Shambling Mound",
            score_args=standard_score_args,
        )


class _VineWhip(PlantPower):
    def __init__(self):
        super().__init__(name="Vine Whip", source="Foe Foundry", icon="vine-whip")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy

        def customize(a: Attack) -> Attack:
            a = a.split_damage(DamageType.Poison, split_ratio=0.9)

            # the ongoing bleed damage should be equal to the poison damage formula for symmetry
            # the damage threshold should be a nice easy multiple of 5 close to half the bleed damage
            bleeding_damage = (
                a.additional_damage.formula
                if a.additional_damage
                else DieFormula.from_expression("1d6")
            )
            threshold = easy_multiple_of_five(bleeding_damage.average / 2, max_val=20)

            bleeding = Bleeding(
                damage=bleeding_damage,
                damage_type=DamageType.Poison,
                dc=dc,
                threshold=threshold,
            )

            a = a.copy(
                additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or gain {bleeding}"
            )
            return a

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            die=Die.d6,
            name="Poison Thorns",
            replaces_multiattack=2,
            callback=customize,
        )

        return stats

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        return stats, []


class _Entangle(PlantPower):
    def __init__(self):
        super().__init__(name="Entangle", source="SRD5.1 Entangle", icon="root-tip")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        spell = conjuration.Entangle.for_statblock(uses=3, notes="no concentration")
        return stats.add_spell(spell=spell)


class _ChokingVine(PlantPower):
    def __init__(self):
        super().__init__(
            name="Choking Vine",
            source="Foe Foundry",
            icon="curling-vines",
            require_attack_types=AttackType.AllMelee(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy
        grappled = Condition.Grappled

        stats = stats.add_attack(
            scalar=1.8,
            damage_type=DamageType.Bludgeoning,
            die=Die.d8,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            name="Choking Vine",
            additional_description=f"On a hit, the target must make a DC {dc} Strength save. On a failure, the creature is {grappled.caption} (escape DC {dc}). \
                While grappled in this way, it cannot speak, cannot breathe, begins choking, and cannot cast spells that require a verbal component.",
        )

        return stats


class _HypnoticSpores(PlantPower):
    def __init__(self):
        super().__init__(
            name="Hypnotic Spores",
            source="SRD5.1 Hypnotic Pattern",
            icon="pollen-dust",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        distance = 30 if stats.difficulty_class <= 7 else 45
        incapacitated = Condition.Incapacitated
        poisoned = Condition.Poisoned
        feature = Feature(
            name="Hypnotic Spores",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} releases a cloud of hypnotic spores. Each non-plant creature within {distance} feet must make a DC {dc} Constitution save. \
                On a failure, the creature is {poisoned.caption} for 1 minute (save ends at end of turn). While poisoned in this way, the target is {incapacitated.caption}",
        )
        return [feature]


class _SpikeGrowth(PlantPower):
    def __init__(self):
        super().__init__(
            name="Spike Growth", icon="spikes-full", source="SRD5.1 Spike Growth"
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        uses = min(3, ceil(stats.cr / 5))

        feature = Feature(
            name="Spike Growth",
            action=ActionType.Action,
            uses=uses,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} releases razor-sharp thorns, creating the effect of a *Spike Growth* spell (without requiring concentration).",
        )

        return [feature]


ChokingVine: Power = _ChokingVine()
Entangle: Power = _Entangle()
HypnoticSpores: Power = _HypnoticSpores()
SpikeGrowth: Power = _SpikeGrowth()
VineWhip: Power = _VineWhip()


PlantPowers: List[Power] = [
    ChokingVine,
    Entangle,
    HypnoticSpores,
    SpikeGrowth,
    VineWhip,
]
