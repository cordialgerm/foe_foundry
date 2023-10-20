from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import HideArmor, NaturalArmor, Unarmored
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from .template import CreatureTypeTemplate


class _GiantTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Giant", creature_type=CreatureType.Giant)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            attack_options = {weapon.Staff: 1, weapon.JavelinAndShield: 1, natural.Lob: 1}
        elif stats.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            attack_options = {
                weapon.JavelinAndShield: 1,
                natural.Lob: 1,
                spell.Firebolt: 1,
                spell.Frostbolt: 1,
                spell.Shock: 1,
            }
        elif stats.role in {MonsterRole.Leader, MonsterRole.Defender}:
            attack_options = {weapon.SpearAndShield: 1, weapon.MaceAndShield: 1}
        else:
            attack_options = {
                natural.Slam: 1,
                weapon.Greatsword: 1,
                weapon.Greataxe: 1,
                weapon.Maul: 1,
            }

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in attack_options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        attack = choices[indx]

        return attack, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: np.random.Generator) -> BaseStatblock:
        # Giants are beefy and don't wear much armor
        # They attack slowly but hit really hard
        dials: dict = dict(hp_multiplier=1.3)

        if stats.multiattack > 2:
            dials.update(multiattack_modifier=-1, attack_damage_modifier=1)

        stats = stats.apply_monster_dials(dials=MonsterDials(**dials))

        # Giants have Strength and Constitution scores as formidable as their size
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(mod=2),
                Stats.DEX: Stats.Scale(8, 1 / 4),
                Stats.INT: Stats.Scale(8, 1 / 3),
                Stats.WIS: Stats.Scale(8, 1 / 2),
                Stats.CHA: Stats.Scale(8, 1 / 2),
            }
        )
        new_attributes = stats.attributes

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)
        if size <= Size.Large:
            size = Size.Large

        # giants with higher CR should have proficiency in STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # giants are often unarmored
        # giants are unarmored or have natural or hide armor
        stats = stats.add_ac_templates([Unarmored, NaturalArmor, HideArmor], ac_modifier=-1)

        return stats.copy(
            creature_type=CreatureType.Giant,
            attributes=new_attributes,
            size=size,
            languages=["Common", "Giant"],
        )


GiantTemplate: CreatureTypeTemplate = _GiantTemplate()
