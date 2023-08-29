# DRAGON

# Senses blindsight 60 ft., darkvision 120 ft.
# Languages Common, Draconic
# A true dragon or a closely related draconic creature
# has a breath weapon that is fearsome to behold. You can
# adjust the damage or area of effect depending on how
# powerful your draconic creature is meant to be.
# Dragon’s Breath (Action, Recharge 5–6). This creature
# breathes to deal poison, cold, or fire damage in a 30-foot cone,
# or breathes to deal acid or lightning damage in a 60-foot line
# that is 5 feet wide. Each creature in the area of the exhalation
# must make a Dexterity saving throw against a line or a
# Constitution saving throw against a cone (DC = 12 + 1/2 CR),
# taking 4 × CR damage of the appropriate type on a failed save,
# or half as much damage on a successful one.
# You might also wish to provide a dragon or draconic
# creature with an additional power to reflect their nature.
# Dragon’s Gaze (Bonus Action, Recharge 6). One creature
# within 60 feet of the dragon must make a Wisdom saving throw
# (DC = 13 + 1/2 CR) or become frightened of the dragon. While
# frightened in this way, each time the target takes damage, they
# take an extra 1/2 CR damage. The target can repeat the saving
# throw at the end of each of their turns, ending the effect on
# themself on a success.
# Dragon’s Gaze puts the pressure on a character, and
# goes well with threats a dragon makes as they promise
# that the heroes are about to meet their doom.

from math import ceil

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorClass, ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _DragonTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Dragon", creature_type=CreatureType.Dragon)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Draconic creatures have high Strength, Dexterity, and
        # Constitution scores, as well as high Charisma scores.
        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.STR
        attrs = {
            Stats.STR: stats.primary_attribute_score,
            Stats.DEX: scale_stat(12, 1 / 2),
            Stats.CON: stats.attributes.CON,
            Stats.INT: scale_stat(10, 1 / 2),
            Stats.WIS: scale_stat(10, 1 / 2),
            Stats.CHA: scale_stat(12, 2 / 3),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

        behavior: str = rng.choice(["lordly", "wise", "predator"])
        if behavior == "lordly":
            new_attributes = new_attributes.grant_proficiency_or_expertise(
                Skills.Perception, Skills.Persuasion, Skills.Deception
            )
        elif behavior == "wise":
            new_attributes = new_attributes.grant_proficiency_or_expertise(
                Skills.Perception, Skills.History, Skills.Insight, Skills.Arcana
            )
        else:
            new_attributes = new_attributes.grant_proficiency_or_expertise(
                Skills.Perception, Skills.Athletics, Skills.Survival
            )

        # dragons have a breath weapon
        attack_type = AttackType.MeleeWeapon
        primary_damage_type = DamageType.Slashing
        breath_weapon_damage_type = choose_enum(
            rng,
            [
                DamageType.Fire,
                DamageType.Lightning,
                DamageType.Acid,
                DamageType.Poison,
                DamageType.Cold,
            ],
        )

        # dragons are immune to their breath weapon
        damage_immunities = stats.damage_immunities | {breath_weapon_damage_type}

        # dragons have blindsight and darkvision
        new_senses = Senses(darkvision=60, blindsight=60)

        # dragons are usually at least Large
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # dragons with higher CR should have proficiency in STR, CON, and DEX saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(
                Stats.STR, Stats.CON, Stats.DEX
            )

        # higher-CR dragons have heavy natural armor
        ac_bonus = ceil(stats.cr / 6)
        new_ac = stats.ac.delta(change=ac_bonus, armor_type=ArmorType.Natural)

        return stats.copy(
            creature_type=CreatureType.Dragon,
            attributes=new_attributes,
            ac=new_ac,
            size=size,
            languages=["Common, Draconic"],
            senses=new_senses,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=breath_weapon_damage_type,
            attack_type=attack_type,
            damage_immunities=damage_immunities,
        )


DragonTemplate: CreatureTypeTemplate = _DragonTemplate()
