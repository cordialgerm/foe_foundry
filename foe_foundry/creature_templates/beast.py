import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _BeastTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Beast", creature_type=CreatureType.Beast)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Beasts might have low ability scores if they are mundane
        # creatures, with their strongest scores in either Strength
        # or Dexterity.
        #
        # They might also have medium to high Wisdom to represent cunning
        #
        # Beasts have low AC and slightly higher CON and HP
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.CON: Stats.Boost(Stats.CON, 2),
                Stats.DEX: Stats.Scale(10, 1 / 2),
                Stats.INT: Stats.Scale(4, 1 / 3),
                Stats.WIS: Stats.Scale(8, 1 / 4),
                Stats.CHA: Stats.Scale(3, 1 / 3),
            }
        )
        new_attributes = stats.attributes

        # updated HP to match CON
        new_hp = stats.hp.copy(mod=stats.hp.n_die * new_attributes.stat_mod(Stats.CON))

        # Beasts typically have darkvision with a 60-foot range
        new_senses = stats.senses.copy(darkvision=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # Beasts attack with melee natural weapons, like claws, bites, and horns
        attack_type = AttackType.MeleeNatural

        primary_damage_types = [
            DamageType.Bludgeoning,  # Hooves, Tail (20%)
            DamageType.Piercing,  #  Bites, Horns (40%)
            DamageType.Slashing,  # Claws (40%)
        ]
        damage_type_indx = rng.choice(3, p=[0.2, 0.4, 0.4])
        primary_damage_type = primary_damage_types[damage_type_indx]

        # beasts with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # beasts are naturally lightly armored
        new_ac = stats.ac.delta(
            change=-2,
            armor_type=ArmorType.Natural,
            shield_allowed=False,
        )

        return stats.copy(
            creature_type=CreatureType.Beast,
            hp=new_hp,
            ac=new_ac,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=None,
            attack_type=attack_type,
        )


BeastTemplate: CreatureTypeTemplate = _BeastTemplate()
