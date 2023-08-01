from foe_foundry.statblocks import BaseStatblock

from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _BeastTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Beast", creature_type=CreatureType.Beast)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        # Beasts might have low ability scores if they are mundane
        # creatures, with their strongest scores in either Strength
        # or Dexterity.
        #
        # They might also have medium to high
        # Constitution or Wisdom to represent hardiness and
        # cunning.

        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.STR
        attrs = {
            Stats.STR: stats.primary_attribute_score,
            Stats.DEX: scale_stat(10, 1 / 2),
            Stats.CON: stats.attributes.CON,
            Stats.INT: scale_stat(4, 1 / 3),
            Stats.WIS: scale_stat(8, 1 / 4),
            Stats.CHA: scale_stat(3, 1 / 3),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

        # Beasts typically have darkvision with a 60-foot range
        new_senses = stats.senses.copy(darkvision=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=self.rng)

        # Beasts attack with melee natural weapons, like claws, bites, and horns
        attack_type = AttackType.MeleeNatural

        primary_damage_types = [
            DamageType.Bludgeoning,  # Hooves, Tail (20%)
            DamageType.Piercing,  #  Bites, Horns (40%)
            DamageType.Slashing,  # Claws (40%)
        ]
        damage_type_indx = self.rng.choice(3, p=[0.2, 0.4, 0.4])
        primary_damage_type = primary_damage_types[damage_type_indx]

        # celestials with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        return stats.copy(
            creature_type=CreatureType.Beast,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=None,
            attack_type=attack_type,
        )


BeastTemplate: CreatureTypeTemplate = _BeastTemplate()
