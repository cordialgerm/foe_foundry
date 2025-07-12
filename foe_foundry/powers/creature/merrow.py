from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import conditions
from ...die import Die
from ...features import ActionType, Feature
from ...spells import CasterType, abjuration, conjuration, evocation, transmutation
from ...statblocks import BaseStatblock
from ..power import (
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


def is_merrow(s: BaseStatblock) -> bool:
    return s.creature_class == "Merrow"


class MerrowPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        icon: str = "fish-monster",
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 6, 6),
        **score_args,
    ):
        super().__init__(
            name=name,
            source="Foe Foundry",
            theme="merrow",
            reference_statblock="Merrow",
            icon=icon,
            power_level=power_level,
            power_category=PowerCategory.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_merrow,
                require_types=CreatureType.Monstrosity,
            )
            | score_args,
        )


class _KelpNets(MerrowPower):
    def __init__(self):
        super().__init__(
            name="Kelp Nets",
            icon="fishing-net",
            power_level=MEDIUM_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        grappled = conditions.Condition.Grappled.caption
        restrained = conditions.Condition.Restrained.caption
        dc = stats.difficulty_class

        feature = Feature(
            name="Kelp Nets",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref.capitalize()} darts forward, deploying a net made of ironstrand kelp. \
                Each creature in a 15 foot cone must make a DC {dc} Strength saving throw or be {grappled} (escape DC {dc}) and {restrained} while the grapple lasts. \
                If the creature does not have a swim speed, it makes any related D20 tests at disadvantage.",
        )

        return [feature]


class _ReelInThePrey(MerrowPower):
    def __init__(self):
        super().__init__(
            name="Reel In The Prey",
            icon="harpoon-chain",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        restrained = conditions.Condition.Restrained.caption
        stats = stats.modify_additional_attack(
            name_or_display_name="Sharktooth Harpoon",
            additional_description=f"On a hit, the target is {restrained} until the end of its next turn.",
        )
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        bleeding_damage = stats.target_value(dpr_proportion=0.25, force_die=Die.d6)
        bleeding = conditions.Bleeding(damage=bleeding_damage)
        restrained = conditions.Condition.Restrained.caption

        feature = Feature(
            name="Reel in the Prey",
            action=ActionType.BonusAction,
            description=f"One creature {restrained} by {stats.selfref} is pulled up to 30 feet closer to {stats.selfref}. \
                The restrained creature may choose to end the condition and not be pulled, \
                but if it does so it takes {bleeding_damage.description} piercing damage and is {bleeding.caption}. {bleeding.description_3rd}",
        )

        return [feature]


class _AnemonePoison(MerrowPower):
    def __init__(self):
        super().__init__(
            name="Anemone Poison",
            icon="poison-bottle",
            power_level=MEDIUM_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(dpr_proportion=0.25, force_die=Die.d6)
        dc = stats.difficulty_class
        poisoned = conditions.Condition.Poisoned.caption

        if stats.cr <= 3:
            uses = 1
            recharge = None
        else:
            uses = None
            recharge = 5

        feature = Feature(
            name="Anemone Poison",
            action=ActionType.BonusAction,
            uses=uses,
            recharge=recharge,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} forces the creature to make a DC {dc} Constitution saving throw. \
                On a failure, the creature is {poisoned} for 1 minute (save ends at end of turn). \
                If the poisoned creature ends its turn submerged in water, it takes {dmg.description} poison damage and automatically fails the save.",
        )
        return [feature]


class _StormblessedMagic(MerrowPower):
    def __init__(self):
        super().__init__(
            name="Stormblessed Magic",
            icon="lightning-storm",
            power_level=MEDIUM_POWER,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)

        stats.grant_spellcasting(caster_type=CasterType.Primal)

        spells = [
            conjuration.Entangle.copy(concentration=False),
            conjuration.SleetStorm,
            abjuration.MassCureWounds,
            evocation.ConeOfCold,
            transmutation.ControlWater,
        ]
        stats = stats.add_spells([s.for_statblock(uses=1) for s in spells])
        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


KelpNets: Power = _KelpNets()
ReelInThePrey: Power = _ReelInThePrey()
AnemonePoison: Power = _AnemonePoison()
StormblessedMagic: Power = _StormblessedMagic()

MerrowPowers: List[Power] = [KelpNets, ReelInThePrey, AnemonePoison, StormblessedMagic]
