from numpy.random import Generator

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..movement import Movement
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _PlantTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Plant", creature_type=CreatureType.Plant)

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # Plants have extremely low mental stats and low Dexterity scores
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(4, 1 / 6),
                Stats.INT: Stats.Scale(1, 1 / 8),
                Stats.WIS: Stats.Scale(4, 1 / 4),
                Stats.CHA: Stats.Scale(1, 1 / 8),
            }
        )
        new_attributes = stats.attributes

        new_movement = Movement(walk=20, climb=20)

        # Plants typically have blindsight with a 30 to 60-foot range
        new_senses = stats.senses.copy(blindsight=30 if stats.cr <= 4 else 60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # Plants attack with melee natural weapons like branches
        attack_type = AttackType.MeleeNatural
        primary_damage_type = DamageType.Bludgeoning
        secondary_damage_type = DamageType.Poison

        condition_immunities = stats.condition_immunities.copy() | {
            Condition.Blinded,
            Condition.Charmed,
            Condition.Prone,
            Condition.Exhaustion,
        }

        # Plants with higher CR should have proficiency in their STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # Plants are naturally heavily armored
        new_ac = stats.ac.delta(
            change=1,
            armor_type=ArmorType.Natural,
            shield_allowed=False,
        )

        return stats.copy(
            creature_type=CreatureType.Plant,
            ac=new_ac,
            speed=new_movement,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=primary_damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            condition_immunities=condition_immunities,
        )

    def customize_role(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # plants that do ranged attacks deal piercing damage
        if stats.attack_type == AttackType.RangedWeapon:
            stats = stats.copy(primary_damage_type=DamageType.Piercing)

        return stats


PlantTemplate: CreatureTypeTemplate = _PlantTemplate()