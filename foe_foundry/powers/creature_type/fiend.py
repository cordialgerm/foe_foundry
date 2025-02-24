from datetime import datetime
from typing import List

import numpy as np

from ...attack_template import natural as natural_attacks
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...spells import enchantment, evocation
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five, summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
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
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Fiend, **score_args)
        super().__init__(
            name=name,
            source=source,
            power_type=PowerType.Creature,
            power_level=power_level,
            create_date=create_date,
            theme="Fiend",
            score_args=standard_score_args,
        )


class _CallOfTheStyx(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Call of the Styx",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
            power_level=HIGH_POWER,
            bonus_damage=DamageType.Cold,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.75)
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


class _FeastOfSouls(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Feast of Souls",
            source="Foe Foundry",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temphp = easy_multiple_of_five(0.1 * stats.hp.average)
        feature = Feature(
            name="Feast of Souls",
            action=ActionType.Reaction,
            description=f"Whenever a creature dies within 120 feet of {stats.selfref} it may choose to gain {temphp} temporary hitpoints, recharge an ability, or regain an expended usage of an ability.",
        )
        return [feature]


class _FiendishCackle(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Cackle", source="Foe Foundry", bonus_damage=DamageType.Fire
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(0.5, force_die=Die.d4)

        dc = stats.difficulty_class
        feature1 = Feature(
            name="Fiendish Cackle",
            action=ActionType.Reaction,
            uses=1,
            description=f"Whenever a creature {stats.selfref} can see fails an attack roll, ability check, or saving throw, {stats.selfref} can use its reaction to cackle maniacally. \
                The creature must make a DC {dc} Wisdom saving throw. On a failure, it takes {dmg.description} fire damage and {stats.selfref} gains that many temporary hitpoints.",
        )

        return [feature1]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        spell = enchantment.Bane.for_statblock(
            uses=1, concentration=False, notes="no concentration"
        )
        return stats.add_spell(spell)


class _FiendishTeleporation(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Teleportation",
            source="Foe Foundry",
            bonus_damage=DamageType.Fire,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        multiplier = 1.25 if stats.multiattack >= 2 else 0.75
        dmg = stats.target_value(multiplier, force_die=Die.d10)
        distance = easy_multiple_of_five(stats.cr * 10, min_val=30, max_val=90)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Fiendish Teleportation",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} disappears and reappears in a burst of flame. It teleports up to {distance} feet to an unoccupied location it can see. \
                {stats.selfref.capitalize()} may choose to bring one friendly creature within 5 feet or a creature it has grappled with it. \
                Each other creature that did not teleport within 10 feet of {stats.selfref} either before or after it teleports must make a DC {dc} Dexterity saving throw. \
                On a failure, it takes {dmg.description} fire damage.",
        )
        return [feature]


class _WallOfFire(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Wall of Fire",
            source="SRD5.1 Wall of Fire",
            require_cr=5,
            bonus_damage=DamageType.Fire,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.cr <= 7:
            uses = 1
            notes = None
        elif stats.cr <= 11:
            uses = 1
            notes = "no concentration"
        else:
            uses = 3
            notes = "no concentration"

        spell = evocation.WallOfFire.for_statblock(uses=uses, notes=notes)

        return stats.add_spell(spell)


class _FiendishBite(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Bite",
            source="Foe Foundry",
            attack_names=natural_attacks.Bite,
            bonus_damage=DamageType.Poison,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class

        def customize(a: Attack) -> Attack:
            return a.split_damage(DamageType.Poison, split_ratio=0.9)

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            name="Fiendish Bite",
            die=Die.d6,
            attack_type=AttackType.MeleeNatural,
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become **Poisoned** for 1 minute (save ends at end of turn).",
            callback=customize,
        )

        return stats


class _FiendishSummons(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Fiendish Summons",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        # TODO - remove randomness
        rng = np.random.default_rng(20210518)
        _, _, description = summoning.determine_summon_formula(
            summoner=summoning.Fiends, summon_cr_target=stats.cr / 2.5, rng=rng
        )

        feature = Feature(
            name="Fiendish Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} summons forth additional fiendish allies. {description}",
        )

        return [feature]


class _TemptingOffer(FiendishPower):
    def __init__(self):
        super().__init__(name="Tempting Offer", source="Foe Foundry", require_cr=3)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Tempting Offer",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} makes a tempting offer to a creature that can hear it within 60 feet. \
                That creature must make a DC {dc} Wisdom saving throw. On a failure, the creature gains a level of **Exhaustion**. \
                The creature may instead accept the offer. In doing so, it loses all levels of exhaustion gained in this way but is contractually bound to the offer",
        )
        return [feature]


class _DevilsSight(FiendishPower):
    def __init__(self):
        super().__init__(
            name="Devil's Sight", source="Foe Foundry", bonus_damage=DamageType.Fire
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        level = 2 if stats.cr <= 5 else 4

        devils_sight = Feature(
            name="Devil's Sight",
            action=ActionType.Feature,
            description=f"Magical darkness doesn't impede {stats.selfref}'s darkvision, and it can see through Hellish Darkness.",
        )

        darkness = Feature(
            name="Hellish Darkness",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes shadowy black flames to fill a 15-foot radius sphere with obscuring darkness centered at a point within 60 feet that {stats.selfref} can see. \
                The darkness spreads around corners. Creatures without Devil's Sight can't see through this darkness and nonmagical light can't illuminate it. \
                If any of this spell's area overlaps with an area of light created by a spell of level {level} or lower, the spell that created the light is dispelled. \
                Creatures of {stats.selfref}'s choice lose any resistance to fire damage while in the darkness, and immunity to fire damage is instead treated as resistance to fire damage.",
        )

        return [devils_sight, darkness]


CallOfTheStyx: Power = _CallOfTheStyx()
DevilsSight: Power = _DevilsSight()
FeastOfSouls: Power = _FeastOfSouls()
FiendishBite: Power = _FiendishBite()
FiendishCackle: Power = _FiendishCackle()
FiendishSummons: Power = _FiendishSummons()
FiendishTeleportation: Power = _FiendishTeleporation()
TemptingOffer: Power = _TemptingOffer()
WallOfFire: Power = _WallOfFire()

FiendishPowers = [
    CallOfTheStyx,
    DevilsSight,
    FeastOfSouls,
    FiendishBite,
    FiendishCackle,
    FiendishSummons,
    FiendishTeleportation,
    TemptingOffer,
    WallOfFire,
]
