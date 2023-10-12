from typing import Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import NaturalArmor
from ..attack_template import AttackTemplate, natural, spell
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from .template import CreatureTypeTemplate


class _AberrationTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Aberration", creature_type=CreatureType.Aberration)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        ranged = 1 if stats.attack_type.is_ranged() else 0
        melee = 1 - ranged

        options = {
            natural.Tentacle: 4 * melee,
            spell.Gaze: 3 * ranged,
            spell.Beam: 3 * ranged,
            natural.Claw: 1 * melee,
            natural.Bite: 1 * melee,
        }
        choices, weights = [], []
        for c, w in options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)

        if melee:
            # melee aberrations still have high charisma but use STR as their primary stat
            stats = stats.scale({Stats.STR: Stats.Primary(), Stats.CHA: Stats.CHA.Boost(-2)})

        # aberrations attack with psychic energy
        stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        return choices[indx], stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
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

        # aberrations with higher CR should have proficiency in CHA and WIS saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        # aberrations use natural armor and tend to not be as heavily armored
        stats = stats.add_ac_template(NaturalArmor).apply_monster_dials(
            MonsterDials(ac_modifier=-1)
        )

        return stats.copy(
            creature_type=CreatureType.Aberration,
            size=size,
            languages=["Deep Speech", "telepathy 120 ft."],
            senses=new_senses,
            attributes=new_attributes,
        )


AberrationTemplate: CreatureTypeTemplate = _AberrationTemplate()
