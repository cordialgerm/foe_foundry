import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import NaturalArmor
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _MonstrosityTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Monstrosity", creature_type=CreatureType.Monstrosity)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.CON: Stats.CON.Boost(2),
                Stats.DEX: Stats.Scale(10, 1 / 2),
                Stats.INT: Stats.Scale(5, 1 / 3),
                Stats.WIS: Stats.Scale(9, 1 / 4),
                Stats.CHA: Stats.Scale(4, 1 / 3),
            }
        )
        new_attributes = stats.attributes

        # updated HP to match CON
        new_hp = stats.hp.copy(mod=stats.hp.n_die * new_attributes.stat_mod(Stats.CON))

        # Monstrosities typically have darkvision with a 60-foot range
        new_senses = stats.senses.copy(darkvision=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # Monstrosity attacks with melee natural weapons, like claws, bites, and horns
        attack_type = AttackType.MeleeNatural
        primary_damage_type = choose_enum(
            rng=rng,
            values=[DamageType.Bludgeoning, DamageType.Piercing, DamageType.Slashing],
            p=[0.2, 0.4, 0.4],
        )

        # Monstrosities with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # monstrosities use natural armor
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=-2)

        return stats.copy(
            creature_type=CreatureType.Monstrosity,
            hp=new_hp,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=None,
            attack_type=attack_type,
        )


MonstrosityTemplate: CreatureTypeTemplate = _MonstrosityTemplate()
