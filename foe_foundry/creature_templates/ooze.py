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


class _OozeTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Ooze", creature_type=CreatureType.Ooze)

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Oozes have low mental stats and low dexterity
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(4, 1 / 4),
                Stats.INT: Stats.Scale(1, 1 / 8),
                Stats.WIS: Stats.Scale(4, 1 / 4),
                Stats.CHA: Stats.Scale(1, 1 / 8),
            }
        )
        new_attributes = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)

        # Oozes typically have blindsight with a 60-foot range
        new_senses = stats.senses.copy(blindsight=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # Oozes attack with melee natural weapons like pseudopods
        attack_type = AttackType.MeleeNatural
        primary_damage_type = DamageType.Bludgeoning
        secondary_damage_type = DamageType.Acid

        condition_immunities = stats.condition_immunities.copy() | {
            Condition.Charmed,
            Condition.Deafened,
            Condition.Exhaustion,
            Condition.Frightened,
            Condition.Prone,
        }

        # Oozes with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # Oozes are naturally lightly armored
        new_ac = stats.ac.delta(
            change=-2,
            armor_type=ArmorType.Natural,
            shield_allowed=False,
        )

        return stats.copy(
            creature_type=CreatureType.Ooze,
            ac=new_ac,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            condition_immunities=condition_immunities,
        )


OozeTemplate: CreatureTypeTemplate = _OozeTemplate()
