from math import ceil
from typing import List, Tuple

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ..ac import flavorful_ac
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType, flavorful_damage_types
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock, MonsterDials
from .power import Power, PowerType
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DamagingAttack(Power):
    """This creature’s attacks deal an extra CR damage of a type appropriate for the creature."""

    def __init__(self):
        super().__init__(name="Damaging Attack", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power can make sense for any monster
        # monsters that use a dedicated weapon or already have a secondary damage type assigned are preferred slightly
        # ambushers get a boost to this as well

        score = MODERATE_AFFINITY

        if candidate.attack_type in {AttackType.MeleeWeapon, AttackType.RangedWeapon}:
            score += LOW_AFFINITY
        if candidate.secondary_damage_type is not None:
            score += LOW_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += LOW_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        # if the monster doesn't already have a damage type, use poison
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        damage_type = stats.secondary_damage_type

        # TODO - integrate this directly into the Attack
        if damage_type == DamageType.Acid:
            name = "Corrosive Attacks"
        elif damage_type == DamageType.Cold:
            name = "Chilling Attacks"
        elif damage_type == DamageType.Fire:
            name = "Superheated Attacks"
        elif damage_type == DamageType.Force:
            name = "Energetic Attacks"
        elif damage_type == DamageType.Lightning:
            name = "Electrified Attacks"
        elif damage_type == DamageType.Necrotic:
            name = "Draining Attacks"
        elif damage_type == DamageType.Poison:
            name = "Poisoned Attacks"
        elif damage_type == DamageType.Psychic:
            name = "Unsettling Attacks"
        elif damage_type == DamageType.Radiant:
            name = "Divine Smite"
        else:
            name = "Damaging Attack"

        dmg = int(ceil(stats.cr))

        feature = Feature(
            name=name,
            description=f"This creature's attacks deal an extra {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )
        return stats, feature


class _Sneaky(Power):
    """Sneaky (Trait). This creature has advantage on Dexterity(Stealth) checks."""

    def __init__(self):
        super().__init__(name="Sneaky", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # this is really good for ambushers that aren't yet expertise in stealth
        if candidate.role != MonsterRole.Ambusher:
            return NO_AFFINITY
        elif Skills.Stealth in candidate.attributes.expertise_skills:
            return NO_AFFINITY  # already has this ability basically
        else:
            return EXTRA_HIGH_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Deception
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Sneaky",
            description="This creature gainst proficiency (or expertise) in Stealth and Deception",
            action=ActionType.Feature,
        )
        return stats, feature


class _Armored(Power):
    """Armored (Trait). This creature gains an additional bonus to its AC."""

    def __init__(self):
        super().__init__(name="Armored", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes sense for most monsters
        # if the monster is already a defender it makes a lot of sense

        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Artillery}:
            return LOW_AFFINITY

        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Leader, MonsterRole.Default}:
            score += HIGH_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        ac_bonus = int(ceil((stats.cr / 5.0)))

        new_ac = flavorful_ac(
            stats.ac.value + ac_bonus, creature_type=stats.creature_type, role=stats.role
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
            or candidate.attributes.INT < 10
            or candidate.attributes.WIS < 10
            or candidate.attributes.CHA < 10
        ):
            return NO_AFFINITY
        else:
            return MODERATE_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature | None]:
        stat_mins = {Stats.CHA: 12, Stats.INT: 12, Stats.WIS: 12}
        stat_bonuses = {Stats.CHA: 2, Stats.INT: 2, Stats.WIS: 2}

        # give the monster reasonable mental stats (min of 12, try to add +2, but don't exceed the creature's primary stat score)
        new_attrs = (
            stats.attributes.update_ranges(
                mins=stat_mins, maxs=stats.primary_attribute_score, bonuses=stat_bonuses
            )
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
            description="This creature has a keen mind. It gains proficiency in Persuasion, Deception, Insight, Intimidation, and Perception, as well as in Wisom, Intelligence, and Charisma saves.",
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
            or candidate.attributes.STR < 10
            or candidate.attributes.DEX < 10
        ):
            return NO_AFFINITY
        else:
            return MODERATE_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature | None]:
        stat_mins = {Stats.STR: 12, Stats.DEX: 12}
        stat_bonuses = {Stats.STR: 2, Stats.DEX: 2}

        # give the monster reasonable physical stats (min of 12, try to add +2, but don't exceed the creature's primary stat score)
        new_attrs = (
            stats.attributes.update_ranges(
                mins=stat_mins, maxs=stats.primary_attribute_score, bonuses=stat_bonuses
            )
            .grant_proficiency_or_expertise(Skills.Athletics, Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX, Stats.STR)
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Athletic",
            description="This creature is athletic. It gains proficiency in Athletics and Acrobatics as well as Strength and Dexterity saves.",
            action=ActionType.Feature,
        )
        return stats, feature


class _ElementalAffinity(Power):
    """This creature is aligned to a particular element"""

    def __init__(self):
        super().__init__(name="Resistant", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # if the monster has a secondary damage type then it's a really good fit
        # otherwise, certain monster types are good fits
        score = 0
        if candidate.secondary_damage_type is not None:
            score += HIGH_AFFINITY
        elif flavorful_damage_types(candidate.creature_type) is not None:
            score += MODERATE_AFFINITY

        return NO_AFFINITY if score == 0 else score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        damage_type = stats.secondary_damage_type

        if damage_type is None:
            candidates = flavorful_damage_types(stats.creature_type)
            if candidates is None:
                raise ValueError("Unexpected Error: this should not happen!")
            i = self.rng.choice(len(candidates))
            damage_type = candidates[i]
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

        dmg = damage_type.name
        feature = Feature(
            name=f"{damage_type.name} Affinity",
            description=f"This creature gains {descr} to {dmg}. It gains advantage on its attacks while it is in an environment where source of {dmg} damage are prevalant.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Speedy(Power):
    def __init__(self):
        super().__init__(name="Speedy", power_type=PowerType.Static)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes sense for monsters with reasonable DEX that aren't defenders
        if candidate.role == MonsterRole.Defender or candidate.attributes.DEX < 10:
            return NO_AFFINITY

        return MODERATE_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature | None]:
        stat_mins = {Stats.DEX: 12}
        stat_bonuses = {Stats.DEX: 2}

        # give the monster reasonable DEX stat (min of 12, try to add +2, but don't exceed the creature's primary stat score)
        new_attrs = (
            stats.attributes.update_ranges(
                mins=stat_mins, maxs=stats.primary_attribute_score, bonuses=stat_bonuses
            )
            .grant_proficiency_or_expertise(Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX)
        )
        stats = stats.copy(attributes=new_attrs).apply_monster_dials(
            MonsterDials(speed_modifier=10)
        )

        feature = Feature(
            name="Speedy",
            action=ActionType.Feature,
            description="This monster's movement increases by 10ft and it gains proficiency in Acrobatics and Dexterity saves",
        )
        return stats, feature


DamagingAttack: Power = _DamagingAttack()
Sneaky: Power = _Sneaky()
Armored: Power = _Armored()
Keen: Power = _Keen()
Athletic: Power = _Athletic()
ElementalAffinity: Power = _ElementalAffinity()
Speedy: Power = _Speedy()

StaticPowers: List[Power] = [
    DamagingAttack,
    Sneaky,
    Armored,
    Keen,
    Athletic,
    ElementalAffinity,
    Speedy,
]


# TODO - organize these
# Grappling Claw Attacks (Chuul)
# Grappling Tentacle Attacks (see above)
# Stinging Poison (Chuul, Wyvern, etc.)
# Bite
# Fist
# Axe
# Club
# Spear
