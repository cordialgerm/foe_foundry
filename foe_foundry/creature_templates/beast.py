from math import floor

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
        #
        # They might also have medium to high
        # Constitution or Wisdom to represent hardiness and
        # cunning.
        #
        #

        # Beasts might have low ability scores if they are mundane
        # creatures, with their strongest scores in either Strength
        # or Dexterity.
        mins = {
            Stats.CHA: 4,
            Stats.INT: 4,
            Stats.WIS: 8,
            Stats.STR: 12,
            Stats.CON: 12,
            Stats.DEX: 12,
        }
        maxs = {
            Stats.CHA: 8,
            Stats.INT: 8,
            Stats.WIS: 14,
            Stats.STR: stats.primary_attribute_score,
            Stats.CON: stats.primary_attribute_score,
            Stats.DEX: stats.primary_attribute_score,
        }
        bonuses = {
            Stats.CHA: -6 + int(floor(stats.cr / 2.0)),
            Stats.INT: -6 + int(floor(stats.cr / 2.0)),
            Stats.WIS: int(floor(stats.cr / 4)),
            Stats.DEX: int(floor(stats.cr / 4)),
            Stats.STR: int(floor(stats.cr / 4)),
            Stats.CON: int(floor(stats.cr / 4)),
        }
        new_attributes = stats.attributes.update_ranges(mins=mins, maxs=maxs, bonuses=bonuses)
        primary_stats = [Stats.STR, Stats.DEX]
        stat_weights = [0.7, 0.3]
        primary_stat_indx = self.rng.choice(2, p=stat_weights)
        primary_stat = primary_stats[primary_stat_indx]

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

        return stats.copy(
            creature_type=CreatureType.Beast,
            size=size,
            languages=None,
            senses=new_senses,
            primary_attribute=primary_stat,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=None,
            attack_type=attack_type,
        )


BeastTemplate: CreatureTypeTemplate = _BeastTemplate()
