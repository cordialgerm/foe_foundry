from math import ceil, floor

import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _UndeadTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Undead", creature_type=CreatureType.Undead)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Plants have extremely low mental stats and low Dexterity scores
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(8, 1 / 4),
                Stats.INT: Stats.Scale(6, 1 / 6),
                Stats.WIS: Stats.Scale(8, 1 / 6),
                Stats.CHA: Stats.Scale(5, 1 / 6),
            }
        )
        new_attributes = stats.attributes

        # Undead either attack with melee weapons or ranged weapons
        attack_type = choose_enum(rng, [AttackType.MeleeWeapon, AttackType.RangedWeapon])
        damage_type = (
            DamageType.Slashing
            if attack_type == AttackType.MeleeWeapon
            else DamageType.Piercing
        )
        secondary_damage_type = DamageType.Necrotic

        # Immunities
        damage_immunities = stats.damage_immunities.copy() | {DamageType.Poison}
        condition_immunities = stats.condition_immunities.copy() | {
            Condition.Exhaustion,
            Condition.Poisoned,
        }

        return stats.copy(
            creature_type=CreatureType.Undead,
            size=Size.Medium,
            languages=[],
            senses=stats.senses.copy(darkvision=60),
            attributes=new_attributes,
            primary_damage_type=damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            damage_immunities=damage_immunities,
            condition_immunities=condition_immunities,
        )


UndeadTemplate: CreatureTypeTemplate = _UndeadTemplate()
