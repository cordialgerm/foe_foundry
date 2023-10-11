from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import Unarmored
from ..attack_template import AttackTemplate, natural, spell
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils import choose_enum
from .template import CreatureTypeTemplate


class _OozeTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Ooze", creature_type=CreatureType.Ooze)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.role in {MonsterRole.Controller, MonsterRole.Artillery}:
            attack_options = {spell.Poisonbolt: 1, spell.Acidsplash: 1}
        else:
            attack_options = {natural.Slam: 1}

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in attack_options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        attack = choices[indx]

        secondary_damage_type = (
            attack.damage_type
            if attack.attack_type and attack.attack_type.is_spell()
            else choose_enum(rng, [DamageType.Acid, DamageType.Poison], p=[3, 1])
        )

        stats = stats.copy(secondary_damage_type=secondary_damage_type)

        return attack, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
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

        # Oozes are unarmored
        stats = stats.add_ac_template(Unarmored)

        return stats.copy(
            creature_type=CreatureType.Ooze,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            condition_immunities=condition_immunities,
        )


OozeTemplate: CreatureTypeTemplate = _OozeTemplate()
