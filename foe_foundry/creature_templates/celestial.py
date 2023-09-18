from math import floor

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _CelestialTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Celestial", creature_type=CreatureType.Celestial)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # As divine beings of the Outer Planes, celestials have  high ability scores.
        # Charisma is often especially high to represent a celestial’s leadership qualities, eloquence, and beauty.
        stats = stats.scale(
            {
                Stats.STR: Stats.Scale(10, 1 / 2),
                Stats.DEX: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(10, 1 / 2),
                Stats.WIS: Stats.Scale(10, 2 / 3),
                Stats.CHA: Stats.Primary(),
            }
        )
        new_attributes = stats.attributes

        # Celestials often have resistance to radiant damage,
        # and they might also have resistance to damage from nonmagical attacks
        damage_resistances = stats.damage_resistances.copy()
        damage_immunities = stats.damage_immunities.copy()
        if stats.cr <= 7:
            nonmagical_resistance = False
            damage_resistances |= {DamageType.Radiant}
        else:
            damage_immunities |= {DamageType.Radiant}
            nonmagical_resistance = True

        # The mightiest celestials possess truesight with a range of 120 feet,
        new_senses = stats.senses.copy(darkvision=120)
        if stats.cr >= 11:
            new_senses = new_senses.copy(truesight=120)

        # Celestials attack with melee weapons like swords imbued with Radiant energy
        attack_type = AttackType.MeleeWeapon
        primary_damage_type = DamageType.Slashing
        secondary_damage_type = DamageType.Radiant

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # celestials may have immunity to the charmed, exhaustion, and frightened conditions.
        condition_immunities = stats.condition_immunities.copy()
        if stats.cr >= 4:
            condition_immunities |= {
                Condition.Charmed,
                Condition.Exhaustion,
                Condition.Frightened,
            }

        # celestials with higher CR should have proficiency in WIS and CHA saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        # celestials use divine armor
        new_ac = stats.ac.delta(
            armor_type=ArmorType.Divine,
            dex=new_attributes.stat_mod(Stats.DEX),
            spellcasting=new_attributes.spellcasting_mod,
        )

        return stats.copy(
            creature_type=CreatureType.Celestial,
            ac=new_ac,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            damage_resistances=damage_resistances,
            damage_immunities=damage_immunities,
            nonmagical_resistance=nonmagical_resistance,
            condition_immunities=condition_immunities,
        )


CelestialTemplate: CreatureTypeTemplate = _CelestialTemplate()
