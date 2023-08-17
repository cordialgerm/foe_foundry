from math import ceil, floor

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils import choose_enum
from .template import CreatureTypeTemplate


class _FiendTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Fiend", creature_type=CreatureType.Fiend)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Ability scores for fiends favor their physical
        # characteristics, though many also have moderate or
        # higher Charisma scores.
        #
        #
        # Demons speak Abyssal, while devils speak
        # Infernal. Both usually have telepathy up to 120 feet.

        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.STR
        attrs = {
            Stats.STR: stats.primary_attribute_score,
            Stats.DEX: scale_stat(10, 1 / 3),
            Stats.CON: stats.attributes.CON,
            Stats.INT: scale_stat(8, 1 / 2),
            Stats.WIS: scale_stat(9, 1 / 2),
            Stats.CHA: scale_stat(10, 2 / 3),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

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

        # Fiends often attack with melee or natural weapons
        attack_type = choose_enum(rng, [AttackType.MeleeNatural, AttackType.MeleeWeapon])
        primary_damage_type = choose_enum(rng, [DamageType.Slashing, DamageType.Piercing])
        secondary_damage_type = DamageType.Fire

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # fiends may have immunity to the poisoned condition.
        condition_immunities = stats.condition_immunities
        if stats.cr >= 4:
            condition_immunities |= {
                Condition.Poisoned,
            }

        # fiends with higher CR should have proficiency in WIS and CHA saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        # fiends use unholy armor and do not carry shields
        new_ac = stats.ac.delta(
            armor_type=ArmorType.Unholy,
            dex=new_attributes.stat_mod(Stats.DEX),
            spellcasting=new_attributes.spellcasting_mod,
            shield_allowed=False,
        )

        return stats.copy(
            creature_type=CreatureType.Fiend,
            ac=new_ac,
            size=size,
            languages=languages,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            damage_resistances=damage_resistances,
            damage_immunities=damage_immunities,
            nonmagical_resistance=nonmagical_resistance,
            nonmagical_immunity=nonmagical_immunity,
            condition_immunities=condition_immunities,
        )


FiendTemplate: CreatureTypeTemplate = _FiendTemplate()
