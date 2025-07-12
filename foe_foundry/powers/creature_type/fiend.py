from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...spells import CasterType, enchantment
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from .. import flags
from ..power import (
    HIGH_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class FiendishPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Fiend, **score_args)
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            create_date=create_date,
            theme="Fiend",
            reference_statblock="Balor",
            icon=icon,
            score_args=standard_score_args,
        )


class _CallOfTheStyx(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Call of the Styx",
            source="Foe Foundry",
            icon="river",
            create_date=datetime(2023, 11, 21),
            power_level=HIGH_POWER,
            bonus_damage=DamageType.Cold,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=1.75)
        dc = stats.difficulty_class
        frozen = conditions.Frozen(dc=dc)
        feature = Feature(
            name="Call of the Styx",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} calls upon the deathly cold waters of the River Styx to drag the souls of the fallen to the lower planes. \
                {stats.selfref.capitalize()} creates a line 60 feet long and 5 feet wide filled with the freezing, life-leeching waters of the Styx. \
                Each creature in the line must make a DC {dc} Strength saving throw. On a failure, a creature takes {dmg.description} cold damage and is pulled up to 60 feet towards {stats.selfref}. \
                If the creature fails by 5 or more, it is also {frozen.caption}. On a success, a creature takes half as much damage and suffers no other effects. {frozen.description_3rd}.",
        )

        return [feature]


class _FiendishCackle(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Cackle",
            source="Foe Foundry",
            icon="imp-laugh",
            bonus_damage=DamageType.Fire,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=0.5, force_die=Die.d4)

        dc = stats.difficulty_class
        feature1 = Feature(
            name="Fiendish Cackle",
            action=ActionType.Reaction,
            uses=1,
            description=f"Whenever a creature {stats.selfref} can see fails an attack roll, ability check, or saving throw, {stats.selfref} can use its reaction to cackle maniacally. \
                The creature must make a DC {dc} Wisdom saving throw. On a failure, it takes {dmg.description} fire damage and {stats.selfref} gains that many temporary hitpoints.",
        )

        return [feature1]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_spellcasting(CasterType.Innate)
        spell = enchantment.Bane.for_statblock(
            uses=1, concentration=False, notes="no concentration"
        )
        return stats.add_spell(spell)


class _FieryTeleporation(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiery Teleportation",
            source="Foe Foundry",
            icon="fire-dash",
            bonus_damage=DamageType.Fire,
            require_no_flags="fiend_teleportation",
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.with_flags("fiend_teleportation", flags.HAS_TELEPORT)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        multiplier = 1.25 if stats.multiattack >= 2 else 0.75
        dmg = stats.target_value(target=multiplier, force_die=Die.d10)
        distance = easy_multiple_of_five(stats.cr * 10, min_val=30, max_val=90)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fiery Teleportation",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} disappears and reappears in a burst of flame. It teleports up to {distance} feet to an unoccupied location it can see. \
                {stats.selfref.capitalize()} may choose to bring one friendly creature within 5 feet or a creature it has grappled with it. \
                Each other creature that did not teleport within 10 feet of {stats.selfref} either before or after it teleports must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} fire damage.",
        )
        return [feature]


class _FiendishTeleporation(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Teleportation",
            source="Foe Foundry",
            icon="body-swapping",
            require_no_flags="fiend_teleportation",
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        return stats.with_flags("fiend_teleportation", flags.HAS_TELEPORT)

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Fiendish Teleportation",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports itself or a friendly creature within 10 feet to an unoccupied space it can see within 60 feet.",
        )
        return [feature]


CallOfTheStyx: Power = _CallOfTheStyx()
FiendishCackle: Power = _FiendishCackle()
FieryTeleportation: Power = _FieryTeleporation()
FiendishTeleportation: Power = _FiendishTeleporation()

FiendishPowers = [
    CallOfTheStyx,
    FiendishCackle,
    FiendishTeleportation,
    FieryTeleportation,
]
