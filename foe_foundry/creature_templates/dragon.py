from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import NaturalArmor
from ..attack_template import AttackTemplate, natural, spell
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _DragonTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Dragon", creature_type=CreatureType.Dragon)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.secondary_damage_type is None:
            raise ValueError("secondary_damage_type is required")

        elemental_attack = spell.attack_template_for_damage(stats.secondary_damage_type)

        options = {}
        if stats.role in {MonsterRole.Controller, MonsterRole.Artillery}:
            options.update({elemental_attack: 1})
        else:
            options.update(
                {
                    natural.Claw: 1,
                    natural.Bite: 1,
                }
            )

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        choice = choices[indx]

        return choice, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
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
            secondary_damage_type=breath_weapon_damage_type,
            damage_immunities=damage_immunities,
        )


DragonTemplate: CreatureTypeTemplate = _DragonTemplate()
