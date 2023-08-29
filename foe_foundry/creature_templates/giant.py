from math import ceil

import numpy as np

from foe_foundry.statblocks import BaseStatblock, MonsterDials

from ..ac import ArmorClass, ArmorType
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _GiantTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Giant", creature_type=CreatureType.Giant)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Giants are beefy and don't wear much armor
        # They attack slowly but hit really hard
        dials: dict = dict(hp_multiplier=1.3, ac_modifier=-2)

        if stats.multiattack > 2:
            dials.update(multiattack_modifier=-1, attack_damage_modifier=1)

        stats = stats.apply_monster_dials(dials=MonsterDials(**dials))

        # Giants have Strength and Constitution scores as formidable as their size
        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.STR
        attrs = {
            Stats.STR: stats.primary_attribute_score + 2,
            Stats.DEX: scale_stat(8, 1 / 4),
            Stats.CON: stats.primary_attribute_score,
            Stats.INT: scale_stat(8, 1 / 3),
            Stats.WIS: scale_stat(8, 1 / 2),
            Stats.CHA: scale_stat(8, 1 / 2),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

        # giants attack with melee weapons like clubs
        attack_type = AttackType.MeleeWeapon
        primary_damage_type = DamageType.Bludgeoning

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)
        if size <= Size.Large:
            size = Size.Large

        # giants with higher CR should have proficiency in STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # giants are often unarmored
        new_ac = stats.ac.delta(armor_type=ArmorType.Unarmored)

        return stats.copy(
            creature_type=CreatureType.Giant,
            attributes=new_attributes,
            ac=new_ac,
            size=size,
            languages=["Common", "Giant"],
            primary_damage_type=primary_damage_type,
            attack_type=attack_type,
        )


GiantTemplate: CreatureTypeTemplate = _GiantTemplate()
