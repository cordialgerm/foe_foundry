from math import floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import HolyArmor
from ..attack_template import AttackTemplate, spell, weapon
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _CelestialTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Celestial", creature_type=CreatureType.Celestial)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        options = {}
        offensive_melee = False
        if stats.role in {MonsterRole.Controller}:
            options.update({spell.HolyBolt: 1})
        elif stats.role in {MonsterRole.Artillery}:
            options.update({weapon.Longbow: 1, spell.HolyBolt: 1})
        elif stats.role in {MonsterRole.Bruiser}:
            offensive_melee = True
            options.update({weapon.Greatsword: 1})
        elif stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            options.update({weapon.SpearAndShield: 1, weapon.Daggers: 0.5})
        else:
            options.update(
                {
                    weapon.SwordAndShield: 1,
                    weapon.MaceAndShield: 1,
                }
            )

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        choice = choices[indx]

        if offensive_melee:
            # melee celestials still have high charisma but use STR as their primary stat
            stats = stats.scale(
                {Stats.STR: Stats.Primary(), Stats.CHA: Stats.Boost(Stats.CHA, -2)}
            )

        # Celestials imbue their attacks with Radiant energy
        stats = stats.copy(secondary_damage_type=DamageType.Radiant)

        return choice, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # As divine beings of the Outer Planes, celestials have  high ability scores.
        # Charisma is often especially high to represent a celestial’s leadership qualities, eloquence, and beauty.
        stats = stats.scale(
            {
                Stats.STR: Stats.Scale(10, 1 / 2),
                Stats.DEX: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(10, 1 / 2),
                Stats.WIS: Stats.Scale(10, 2 / 3),
                Stats.CHA: Stats.Primary(),
            }
        )
        new_attributes = stats.attributes

        # Celestials often have resistance to radiant damage,
        # and they might also have resistance to damage from nonmagical attacks
        if stats.cr <= 7:
            stats = stats.grant_resistance_or_immunity(resistances={DamageType.Radiant})
        else:
            stats = stats.grant_resistance_or_immunity(
                immunities={DamageType.Radiant}, nonmagical_resistance=True
            )

        # The mightiest celestials possess truesight with a range of 120 feet,
        new_senses = stats.senses.copy(darkvision=120)
        if stats.cr >= 11:
            new_senses = new_senses.copy(truesight=120)

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # celestials may have immunity to the charmed, exhaustion, and frightened conditions.
        if stats.cr >= 4:
            stats = stats.grant_resistance_or_immunity(
                conditions={
                    Condition.Charmed,
                    Condition.Exhaustion,
                    Condition.Frightened,
                }
            )

        # celestials with higher CR should have proficiency in WIS and CHA saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.CHA, Stats.WIS)

        stats = stats.add_ac_template(HolyArmor)

        return stats.copy(
            creature_type=CreatureType.Celestial,
            size=size,
            languages=["Common", "Celestial", "Telepathy 120 ft"],
            senses=new_senses,
            attributes=new_attributes,
        )


CelestialTemplate: CreatureTypeTemplate = _CelestialTemplate()
