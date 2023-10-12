from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import UnholyArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils import choose_enum
from .template import CreatureTypeTemplate


class _FiendTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Fiend", creature_type=CreatureType.Fiend)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            attack_options = {natural.Claw: 4, natural.Bite: 2, natural.Tail: 1}
        elif stats.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            attack_options = {
                spell.Firebolt: 3,
                spell.Poisonbolt: 1,
                spell.Deathbolt: 1,
                spell.Frostbolt: 1,
            }
        elif stats.role in {MonsterRole.Leader}:
            attack_options = {weapon.Whip: 1, weapon.Staff: 1, weapon.Greatsword: 1}
        else:
            attack_options = {
                natural.Claw: 1,
                weapon.Greatsword: 1,
                weapon.Greataxe: 1,
                weapon.Maul: 1,
            }

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in attack_options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        attack = choices[indx]

        secondary_damage_type = (
            attack.damage_type
            if attack.attack_type is not None and attack.attack_type.is_spell()
            else choose_enum(rng, [DamageType.Fire, DamageType.Poison], [3, 1])
        )
        stats = stats.copy(secondary_damage_type=secondary_damage_type)

        return attack, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # Ability scores for fiends favor their physical
        # characteristics, though many also have moderate or
        # higher Charisma scores.
        #
        #
        # Demons speak Abyssal, while devils speak
        # Infernal. Both usually have telepathy up to 120 feet.
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(8, 1 / 2),
                Stats.WIS: Stats.Scale(9, 1 / 2),
                Stats.CHA: Stats.Scale(10, 2 / 3),
            }
        )
        new_attributes = stats.attributes

        # Devils hoping to entice mortals into deals also often have proficiency in the Deception skill.
        new_attributes = new_attributes.grant_proficiency_or_expertise(Skills.Deception)

        # Fiends typically have resistance to nonmagical attacks, and might have one or more elemental resistances.
        elements = [DamageType.Lightning, DamageType.Cold, DamageType.Poison]
        n = min(floor(stats.cr * 2 / 3), len(elements))
        chosen_elements = set()
        if n > 0:
            chosen_elements.update(choose_enum(rng, elements, size=n, replace=False))

        if stats.cr <= 2:
            nonmagical_resistance = False
            nonmagical_immunity = False
            damage_resistances = chosen_elements | {DamageType.Fire}
            damage_immunities = set()
        elif stats.cr <= 9:
            nonmagical_resistance = True
            nonmagical_immunity = False
            damage_resistances = chosen_elements - {DamageType.Fire}
            damage_immunities = {DamageType.Fire}
        else:
            nonmagical_resistance = False
            nonmagical_immunity = True
            damage_resistances = set()
            damage_immunities = chosen_elements | {DamageType.Fire}

        # fiends speak abyssal or infernal and use telepathy
        languages = [rng.choice(["Abyssal", "Infernal"]), "telepathy 120 ft."]

        # Fiends possess darkvision
        new_senses = stats.senses.copy(darkvision=120)

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # fiends may have immunity to the poisoned condition.
        condition_immunities = stats.condition_immunities.copy()
        if stats.cr >= 4:
            condition_immunities |= {
                Condition.Poisoned,
            }

        # fiends with higher CR should have proficiency in WIS and CHA saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        # fiends use unholy armor
        stats = stats.add_ac_template(UnholyArmor)

        return stats.copy(
            creature_type=CreatureType.Fiend,
            size=size,
            languages=languages,
            senses=new_senses,
            attributes=new_attributes,
            damage_resistances=damage_resistances,
            damage_immunities=damage_immunities,
            nonmagical_resistance=nonmagical_resistance,
            nonmagical_immunity=nonmagical_immunity,
            condition_immunities=condition_immunities,
        )


FiendTemplate: CreatureTypeTemplate = _FiendTemplate()
