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


class _FeyTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Fey", creature_type=CreatureType.Fey)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Fey often have high Charisma and Dexterity scores and moderate-to-high Wisdom scores.
        def scale_stat(base: int, cr_multiplier: float) -> int:
            new_stat = int(round(base + stats.cr * cr_multiplier))
            return min(new_stat, stats.primary_attribute_score)

        primary_stat = Stats.DEX
        attrs = {
            Stats.STR: scale_stat(8, 1 / 3),
            Stats.DEX: stats.primary_attribute_score,
            Stats.CON: stats.attributes.CON,
            Stats.INT: scale_stat(10, 1 / 3),
            Stats.WIS: scale_stat(12, 1 / 2),
            Stats.CHA: scale_stat(12, 1 / 2),
        }
        new_attributes = stats.attributes.copy(**attrs, primary_attribute=primary_stat)

        # Most fey have proficiency in the Deception, Perception, or Persuasion skills.
        skills = choose_enum(
            rng,
            [Skills.Deception, Skills.Persuasion, Skills.Perception],
            size=min(3, ceil(stats.cr / 3)),
        )
        new_attributes = new_attributes.grant_proficiency_or_expertise(*skills)

        # Fey either attack with melee weapons or ranged weapons
        attack_type = choose_enum(rng, [AttackType.MeleeWeapon, AttackType.RangedWeapon])
        damage_type = DamageType.Piercing

        # fey are often lightly armored but are dextrous
        new_ac = stats.ac.delta(
            armor_type=ArmorType.Light,
            shield_allowed=True,
            dex=new_attributes.stat_mod(Stats.DEX),
        )

        return stats.copy(
            creature_type=CreatureType.Fey,
            ac=new_ac,
            size=Size.Medium,
            languages=["Common", "Elvish", "Sylvan"],
            senses=stats.senses.copy(darkvision=60),
            attributes=new_attributes,
            primary_damage_type=damage_type,
            attack_type=attack_type,
        )


FeyTemplate: CreatureTypeTemplate = _FeyTemplate()
