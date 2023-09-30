from math import ceil

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import NaturalArmor
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
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(12, 1 / 2),
                Stats.INT: Stats.Scale(10, 1 / 2),
                Stats.WIS: Stats.Scale(10, 1 / 2),
                Stats.CHA: Stats.Scale(12, 2 / 3),
            }
        )
        new_attributes = stats.attributes

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
        damage_immunities = stats.damage_immunities.copy() | {breath_weapon_damage_type}

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
        ac_bonus = min(ceil(stats.cr / 7), 2)
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=ac_bonus)
        return stats.copy(
            creature_type=CreatureType.Dragon,
            attributes=new_attributes,
            size=size,
            languages=["Common, Draconic"],
            senses=new_senses,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=breath_weapon_damage_type,
            attack_type=attack_type,
            damage_immunities=damage_immunities,
        )


DragonTemplate: CreatureTypeTemplate = _DragonTemplate()
