import numpy as np
from numpy.random import Generator

from ..ac_templates import NaturalArmor, Unarmored
from ..attack_template import AttackTemplate, natural
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from .template import CreatureTypeTemplate


class _BeastTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Beast", creature_type=CreatureType.Beast)

    def select_attack_template(self, stats: BaseStatblock, rng: Generator) -> AttackTemplate:
        # beasts attack with natural weapons
        if stats.attack_type.is_ranged():
            choices = [
                natural.Spit,
                natural.Spines,
            ]
            weights = [1, 1]
        else:
            choices = [
                natural.Bite,
                natural.Claw,
                natural.Horns,
                natural.Stomp,
                natural.Tail,
                natural.Stinger,
                natural.Slam,
            ]
            weights = [3, 3, 2, 1, 1, 1, 0.5]

        weights = np.array(weights, dtype=float) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        return choices[indx]

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
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

        # beasts with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # beasts are either unarmored or have light natural armor
        stats = stats.add_ac_templates([Unarmored, NaturalArmor], ac_modifier=-4)

        return stats.copy(
            creature_type=CreatureType.Beast,
            hp=new_hp,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
        )


BeastTemplate: CreatureTypeTemplate = _BeastTemplate()
