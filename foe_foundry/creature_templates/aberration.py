import numpy as np

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _AberrationTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Aberration", creature_type=CreatureType.Aberration)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Aberrations generally have high mental stats
        # this means the minimum stat value should be 12 for mental stats
        # we should also boost mental stat scores
        stats = stats.scale(
            {
                Stats.CHA: Stats.Primary(),
                Stats.WIS: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(10, 1 / 4),
                Stats.DEX: Stats.Scale(8, 1 / 3),
                Stats.STR: Stats.Scale(8, 1 / 5),
            }
        )
        new_attributes = stats.attributes

        new_senses = stats.senses.copy(darkvision=120)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Medium, rng=rng)

        attack_types = [AttackType.MeleeNatural, AttackType.RangedSpell]
        attack_weights = [0.6, 0.4]
        attack_indx = rng.choice(2, p=attack_weights)
        attack_type = attack_types[attack_indx]

        primary_damage_type = (
            DamageType.Bludgeoning
            if attack_type == AttackType.MeleeNatural
            else DamageType.Psychic
        )
        secondary_damage_type = DamageType.Psychic

        # aberrations with higher CR should have proficiency in CHA and WIS saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        # aberrations have natural armor and do not wear shields
        new_ac = stats.ac.delta(
            armor_type=ArmorType.Natural,
            shield_allowed=False,
            dex=stats.attributes.stat_mod(Stats.DEX),
            spellcasting=stats.attributes.spellcasting_mod,
        )

        return stats.copy(
            creature_type=CreatureType.Aberration,
            ac=new_ac,
            size=size,
            languages=["Deep Speech", "telepathy 120 ft."],
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
        )


AberrationTemplate: CreatureTypeTemplate = _AberrationTemplate()
