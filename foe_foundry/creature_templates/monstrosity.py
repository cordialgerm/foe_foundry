import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
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
        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.STR
        attrs = {
            Stats.STR: stats.primary_attribute_score,
            Stats.DEX: scale_stat(10, 1 / 2),
            Stats.CON: stats.attributes.CON + 2,
            Stats.INT: scale_stat(5, 1 / 3),
            Stats.WIS: scale_stat(9, 1 / 4),
            Stats.CHA: scale_stat(4, 1 / 3),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

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

        # monstrosities are naturally lightly armored
        new_ac = stats.ac.delta(
            change=-2,
            armor_type=ArmorType.Natural,
            shield_allowed=False,
        )

        return stats.copy(
            creature_type=CreatureType.Monstrosity,
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


MonstrosityTemplate: CreatureTypeTemplate = _MonstrosityTemplate()
