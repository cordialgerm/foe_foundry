from typing import Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import NaturalArmor
from ..attack_template import AttackTemplate, natural, spell
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..movement import Movement
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _PlantTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Plant", creature_type=CreatureType.Plant)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher, MonsterRole.Controller}:
            options = [natural.Thrash]
        elif stats.role in {MonsterRole.Artillery}:
            options = [natural.Spines, spell.Poisonbolt]
        elif stats.role in {MonsterRole.Bruiser, MonsterRole.Defender, MonsterRole.Leader}:
            options = [natural.Slam]
        else:
            raise ValueError(f"Unsupported role {stats.role}")

        index = rng.choice(len(options))
        attack = options[index]
        return attack, stats

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

        # Plants are naturally armored
        stats = stats.add_ac_template(NaturalArmor)

        return stats.copy(
            creature_type=CreatureType.Plant,
            speed=new_movement,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            condition_immunities=condition_immunities,
        )


PlantTemplate: CreatureTypeTemplate = _PlantTemplate()
