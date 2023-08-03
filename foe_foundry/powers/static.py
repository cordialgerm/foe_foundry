from math import ceil
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorClass, ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock, MonsterDials
from .attack import flavorful_damage_types
from .power import Power, PowerType
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Armored(Power):
    """Armored (Trait). This creature gains an additional bonus to its AC."""

    def __init__(self):
        super().__init__(name="Armored", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes sense for most monsters
        # if the monster is already a defender it makes a lot of sense

        if candidate.role in {
            MonsterRole.Ambusher,
            MonsterRole.Artillery,
            MonsterRole.Skirmisher,
        } or not ArmorClass.could_use_shield_or_wear_armor(candidate.creature_type):
            return NO_AFFINITY

        score = LOW_AFFINITY
        if candidate.role in {MonsterRole.Leader, MonsterRole.Defender}:
            score += MODERATE_AFFINITY

        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        ac_bonus = int(ceil((stats.cr / 5.0)))
        has_shield = ArmorClass.could_use_shield_or_wear_armor(stats.creature_type)
        target_ac = stats.ac.value + ac_bonus + (2 if has_shield else 0)
        armor_type = ArmorType.Heavy if has_shield else stats.ac.armor_type

        new_ac = ArmorClass(
            value=target_ac, armor_type=armor_type, quality=ac_bonus, has_shield=has_shield
        )

        feature = Feature(
            name="Armored",
            description=f"This creature is heavily armored. It gains a bonus to its AC of {ac_bonus} (included in AC)",
            action=ActionType.Feature,
        )

        stats = stats.copy(ac=new_ac)
        return stats, feature


class _Keen(Power):
    """This creature has a keen mind"""

    def __init__(self):
        super().__init__(name="Keen", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # This power makes sense for any non-beast monster with reasonable mental stats

        if (
            candidate.creature_type == CreatureType.Beast
            or candidate.role == MonsterRole.Bruiser
            or candidate.attributes.INT <= 10
            or candidate.attributes.WIS <= 10
            or candidate.attributes.CHA <= 10
        ):
            return NO_AFFINITY
        else:
            return MODERATE_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        # give the monster reasonable mental stats
        new_attrs = (
            stats.attributes.boost(Stats.CHA, 2)
            .boost(Stats.INT, 2)
            .boost(Stats.WIS, 2)
            .grant_proficiency_or_expertise(
                Skills.Persuasion,
                Skills.Deception,
                Skills.Insight,
                Skills.Intimidation,
                Skills.Perception,
            )
            .grant_save_proficiency(Stats.WIS, Stats.INT, Stats.CHA)
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Keen Mind",
            description="This creature has a keen mind. It gains proficiency in Persuasion, Deception, Insight, Intimidation, and Perception, as well as in Wisdom, Intelligence, and Charisma saves.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Athletic(Power):
    """This creature is Athletic"""

    def __init__(self):
        super().__init__(name="Athletic", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # this makes sense for most monsters with reasonable physical stats except artillery or controllers
        if (
            candidate.role == MonsterRole.Artillery
            or candidate.role == MonsterRole.Controller
            or candidate.attributes.STR <= 10
            or candidate.attributes.DEX <= 10
        ):
            return NO_AFFINITY
        else:
            return MODERATE_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        # give the monster reasonable physical stats
        new_attrs = (
            stats.attributes.boost(Stats.STR, 2)
            .grant_proficiency_or_expertise(Skills.Athletics)
            .grant_save_proficiency(Stats.STR)
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Athletic",
            description="This creature is athletic. It gains proficiency in Athletics and Strength saves.",
            action=ActionType.Feature,
        )
        return stats, feature


class _ElementalAffinity(Power):
    """This creature is aligned to a particular element"""

    def __init__(self):
        super().__init__(name="ElementalAffinity", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # if the monster has a secondary damage type then it's a good fit
        # otherwise, certain monster types are good fits
        score = 0
        if candidate.secondary_damage_type is not None:
            score += MODERATE_AFFINITY
        elif flavorful_damage_types(candidate) is not None:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type

        if damage_type is None:
            candidates = flavorful_damage_types(stats, default=DamageType.Fire)
            i = rng.choice(len(candidates))
            damage_type = list(candidates)[i]
            stats = stats.copy(secondary_damage_type=damage_type)

        if stats.cr <= 8 and damage_type not in stats.damage_resistances:
            new_damage_resistances = stats.damage_resistances | {damage_type}
            stats = stats.copy(damage_resistances=new_damage_resistances)
            descr = "resistance"
        else:
            new_damage_resistances = stats.damage_resistances - {damage_type}
            new_damage_immunities = stats.damage_immunities | {damage_type}
            descr = "immunity"
            stats = stats.copy(
                damage_resistances=new_damage_resistances,
                damage_immunities=new_damage_immunities,
            )

        dmg = damage_type.name.lower()
        feature = Feature(
            name=f"{damage_type.name} Affinity",
            description=f"{stats.selfref} gains {descr} to {dmg}. It gains advantage on its attacks while it is in an environment where sources of {dmg} damage are prevalant.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Gigantic(Power):
    """Increases the size and damage of the creature but lowers its AC"""

    def __init__(self):
        super().__init__(name="Gigantic", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Ambusher}:
            return NO_AFFINITY
        if candidate.creature_type in {
            CreatureType.Beast,
            CreatureType.Monstrosity,
            CreatureType.Construct,
        }:
            score += EXTRA_HIGH_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Bruiser}:
            score += HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = (
            stats.attributes.grant_save_proficiency(Stats.STR)
            .grant_proficiency_or_expertise(Skills.Athletics)
            .change_primary(Stats.STR)
        )

        stats = stats.copy(
            size=stats.size.increment(), attributes=new_attrs
        ).apply_monster_dials(dials=MonsterDials(ac_modifier=-2, attack_damage_dice_modifier=1))

        feature = Feature(
            name="Gigantic",
            action=ActionType.Feature,
            description="This creature is one size larger than its usual kin.",
        )
        return stats, feature


class _Diminutive(Power):
    """Decreases the size and damage of the creature but increases its AC"""

    def __init__(self):
        super().__init__(name="Diminutive", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        score = 0
        if candidate.role in {MonsterRole.Bruiser} or candidate.creature_type in {
            CreatureType.Giant
        }:
            return NO_AFFINITY
        elif candidate.creature_type in {CreatureType.Humanoid, CreatureType.Fey}:
            score += HIGH_AFFINITY
        elif candidate.role in {
            MonsterRole.Ambusher,
            MonsterRole.Controller,
            MonsterRole.Skirmisher,
        }:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = (
            stats.attributes.grant_proficiency_or_expertise(Skills.Stealth, Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX)
            .change_primary(Stats.DEX)
        )

        stats = stats.copy(
            size=stats.size.decrement(), attributes=new_attrs
        ).apply_monster_dials(dials=MonsterDials(ac_modifier=2, attack_damage_modifier=-1))

        feature = Feature(
            name="Diminutive",
            action=ActionType.Feature,
            description="This creature is one size smaller than its kin",
        )
        return stats, feature


Armored: Power = _Armored()
Keen: Power = _Keen()
Athletic: Power = _Athletic()
ElementalAffinity: Power = _ElementalAffinity()
Gigantic: Power = _Gigantic()
Diminutive: Power = _Diminutive()


StaticPowers: List[Power] = [
    Armored,
    Keen,
    Athletic,
    ElementalAffinity,
    Gigantic,
    Diminutive,
]

# TODO - additional ideas

# Perceptive (perception proficiency / expertise)
# Hunter (survival proficiency / expertise)
# Beasts often  have the ability to climb, swim, or fly, and they might be
