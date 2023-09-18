from math import floor

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _ElementalTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Elemental", creature_type=CreatureType.Elemental)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Elementals generally have strong physical ability scores
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(5, 1 / 3),
                Stats.WIS: Stats.Scale(7, 1 / 2),
                Stats.CHA: Stats.Scale(8, 1 / 2),
            }
        )
        new_attributes = stats.attributes

        elemental_type = choose_enum(
            rng,
            [
                DamageType.Fire,
                DamageType.Lightning,
                DamageType.Acid,
                DamageType.Poison,
                DamageType.Cold,
            ],
        )

        attack_type = AttackType.MeleeNatural

        damage_resistances = stats.damage_resistances.copy()
        damage_immunities = stats.damage_immunities.copy()
        if stats.cr <= 7:
            damage_resistances |= {elemental_type}
            damage_immunities |= {DamageType.Poison}
        else:
            damage_immunities |= {elemental_type, DamageType.Poison}

        condition_immunities = {
            Condition.Poisoned,
            Condition.Exhaustion,
            Condition.Grappled,
            Condition.Paralyzed,
            Condition.Petrified,
            Condition.Prone,
            Condition.Restrained,
        }

        new_senses = stats.senses.copy(darkvision=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Medium, rng=rng)

        # elementals have natural armor
        new_ac = stats.ac.delta(armor_type=ArmorType.Natural)

        return stats.copy(
            creature_type=CreatureType.Elemental,
            ac=new_ac,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=elemental_type,
            secondary_damage_type=elemental_type,
            attack_type=attack_type,
            damage_resistances=damage_resistances,
            damage_immunities=damage_immunities,
            nonmagical_resistance=True,
            condition_immunities=condition_immunities,
        )


ElementalTemplate: CreatureTypeTemplate = _ElementalTemplate()
