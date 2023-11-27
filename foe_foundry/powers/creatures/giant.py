from datetime import datetime
from math import ceil
from typing import List

from ...attack_template import natural
from ...attributes import Skills
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Dazed, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class GiantPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_types=CreatureType.Giant, bonus_size=Size.Huge, **score_args
        )
        super().__init__(
            name=name,
            power_type=PowerType.Creature,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Giant",
            score_args=standard_score_args,
        )


class _Boulder(GiantPower):
    def __init__(self):
        super().__init__(name="Boulder", source="SRD 5.1 Hill Giant")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        if stats.multiattack >= 3:
            target = 1.5
        else:
            target = 1.25

        dmg = stats.target_value(target, suggested_die=stats.size.hit_die())

        if stats.cr >= 12:
            distance = 60
            radius = 20
        elif stats.cr >= 8:
            distance = 45
            radius = 15
        elif stats.cr >= 4:
            distance = 30
            radius = 10
        else:
            distance = 20
            radius = 5

        feature = Feature(
            name="Boulder",
            action=ActionType.Action,
            recharge=4,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} tosses a boulder at a point it can see within {distance} ft. Each creature within a {radius} ft radius must make a DC {dc} Dexterity saving throw. \
                On a failure, the creature takes {dmg.description} bludgeoning damage and is knocked prone. On a success, the creature takes half damage and is not knocked prone.",
        )
        return [feature]


# TODO A5E SRD - can these runes be linked to A5E SRD?


class _CloudRune(GiantPower):
    def __init__(self):
        super().__init__(name="Cloud Rune", source="FoeFoundryOriginal")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Cloud Rune",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} or a creature it can see is hit by an attack roll, {stats.selfref} can invoke a Cloud Rune \
                and choose a different creature within 30 feet of {stats.selfref}. The chosen creature becomes the target of the attack. \
                This magic can transfer the attack's effect regardless of the attack's range.",
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Lightning}, upgrade_resistance_to_immunity_if_present=True
        )

        new_attributes = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(
            secondary_damage_type=DamageType.Lightning, attributes=new_attributes
        )

        return stats


class _FireRune(GiantPower):
    def __init__(self):
        super().__init__(
            name="Fire Rune",
            source="FoeFoundryOriginal",
            power_level=LOW_POWER,
            bonus_damage=DamageType.Fire,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(target=0.33, suggested_die=Die.d6)
        burning = conditions.Burning(dmg)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Fire Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} invokes the fire run. \
                The target takes an extra {dmg.description} fire damage and must make a DC {dc} Strength save. On a failure, the creature is **Restrained** (save ends at end of turn). \
                While restrained in this way, the creature is {burning.caption}. {burning.description_3rd}",
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Fire}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Fire)
        return stats


class _FrostRune(GiantPower):
    def __init__(self):
        super().__init__(
            name="Frost Rune",
            source="FoeFoundryOriginal",
            power_level=LOW_POWER,
            bonus_damage=DamageType.Cold,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        dmg = int(ceil(0.5 * stats.attack.average_damage))
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Frost Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} invokes the frost run. \
                The target takes an extra {dmg} cold damage and must make a DC {dc} Constitution save or become {frozen.caption}. \
                {frozen.description_3rd}",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Cold}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Cold)
        return stats


class _StoneRune(GiantPower):
    def __init__(self):
        super().__init__(name="Stone Rune", source="FoeFoundryOriginal", power_level=LOW_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Stone Rune",
            action=ActionType.Reaction,
            uses=1,
            description=f"When a creature ends its turn within 30 feet of {stats.selfref}, {stats.selfref} can activate the stone rune. \
                The creature must make a DC {dc} Wisdom save. On a failure, the creature is **Charmed** for 1 minute (save ends at end of turn). \
                While charmed in this way, the creature is **Incapacitated** in a dreamy stupor.",
        )
        return [feature]


class _HillRune(GiantPower):
    def __init__(self):
        super().__init__(name="Hill Rune", source="FoeFoundryOriginal")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Hill Rune",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} invokes the hill rune and gains resistance to bludgeoning, piercing, and slashing damage for 1 minute",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Poison}, upgrade_resistance_to_immunity_if_present=True
        )
        return stats


class _StormRune(GiantPower):
    def __init__(self):
        super().__init__(name="Storm Rune", source="FoeFoundryOriginal", power_level=LOW_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Storm Rune",
            action=ActionType.Reaction,
            uses=3,
            description=f"Whenever {stats.selfref} or another creature makes an attack roll, saving throw, or ability check, {stats.selfref} can force the roll to have advantage or disadvantage.",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(
            resistances={DamageType.Lightning}, upgrade_resistance_to_immunity_if_present=True
        )
        stats = stats.copy(secondary_damage_type=DamageType.Lightning)
        return stats


class _Earthshaker(GiantPower):
    def __init__(self):
        super().__init__(
            name="Earthshaker", source="FoeFoundryOriginal", attack_names=natural.Slam
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        size = stats.size.decrement().decrement() if stats.size >= Size.Huge else Size.Medium
        distance1 = easy_multiple_of_five(1.5 * stats.cr, min_val=10, max_val=30)

        sizes = {Size.Gargantuan: 60, Size.Huge: 45, Size.Large: 30}
        distance2 = sizes.get(stats.size, 15)

        dazed = Dazed()

        feature1 = Feature(
            name="Earthshaker",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} moves, all {size} or smaller creatures that are within {distance1} feet of {stats.selfref} \
                must make a DC {dc} Strength check or fall **Prone**. A creature that falls prone in this way loses concentration.",
        )

        dmg = stats.target_value(1.5, force_die=Die.d8)

        feature2 = Feature(
            name="Earthshaker Stomp",
            action=ActionType.Action,
            replaces_multiattack=2,
            uses=1,
            description=f"{stats.selfref.capitalize()} stomps its foot, creathing a massive shockwave. Each creature in a {distance2} ft cone \
                must make a DC {dc} Strength saving throw or take {dmg.description} Thunder damage and be {dazed}",
        )

        return [feature1, feature2]


class _BigWindup(GiantPower):
    def __init__(self):
        super().__init__(
            name="Big Windup",
            source="A5E SRD Cyclops",
            create_date=datetime(2023, 11, 22),
            require_attack_types=AttackType.AllMelee(),
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Big Windup",
            action=ActionType.Reaction,
            description=f"Whenever a creature hits {stats.selfref} with a melee attack, {stats.selfref} readies a powerful strike against its attacker. \
                {stats.selfref} has advantage on the next attack it makes against the attacker before the end of its next turn.",
        )
        return [feature]


BigWindup: Power = _BigWindup()
Boulder: Power = _Boulder()
CloudRune: Power = _CloudRune()
Earthshaker: Power = _Earthshaker()
FireRune: Power = _FireRune()
FrostRune: Power = _FrostRune()
HillRune: Power = _HillRune()
StoneRune: Power = _StoneRune()
StormRune: Power = _StormRune()


GiantPowers: List[Power] = [
    BigWindup,
    Boulder,
    CloudRune,
    Earthshaker,
    FireRune,
    FrostRune,
    HillRune,
    StoneRune,
    StormRune,
]
