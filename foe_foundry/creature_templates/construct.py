from math import ceil
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import LightArmor, MediumArmor, NaturalArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from .template import CreatureTypeTemplate


class _ConstructTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Construct", creature_type=CreatureType.Construct)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        options = {}
        if stats.role in {MonsterRole.Ambusher}:
            options.update({weapon.Traps: 1})
        elif stats.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            options.update(
                {
                    spell.Firebolt: 1,
                    spell.Poisonbolt: 1,
                    spell.Frostbolt: 1,
                    spell.Shock: 1,
                    spell.Acidsplash: 1,
                }
            )
        else:
            options.update(
                {natural.Slam: 3, weapon.Greataxe: 1, weapon.Greatsword: 1, weapon.Maul: 1}
            )

        # Constructs attack with melee weapons like swords
        choices: List[AttackTemplate] = []
        weights = []
        for c, w in options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        choice = choices[indx]
        return choice, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # have either blindsight or darkvision, and a selection of
        # damage immunities and condition immunities to reflect
        # their nonliving nature. They usually can’t speak, but might
        # understand one or more languages.

        # A construct’s strongest ability scores are usually Strength and Constitution
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(8, 1 / 3),
                Stats.INT: Stats.Scale(4, 1 / 3),
                Stats.WIS: Stats.Scale(8, 1 / 4),
                Stats.CHA: Stats.Scale(2, 1 / 3),
            }
        )
        new_attributes = stats.attributes

        # Damage Immunities poison, psychic
        # Condition Immunities blinded, charmed, deafened,
        # exhaustion, frightened, paralyzed, petrified, poisoned
        stats = stats.grant_resistance_or_immunity(
            immunities={
                DamageType.Poison,
                DamageType.Psychic,
            },
            nonmagical_resistance=stats.cr >= 7,
            conditions={
                Condition.Exhaustion,
                Condition.Frightened,
                Condition.Paralyzed,
                Condition.Petrified,
                Condition.Poisoned,
            },
        )

        # Senses blindsight 60 ft. (blind beyond this radius) or
        # darkvision 60 ft.
        if stats.cr <= 7:
            new_senses = Senses(darkvision=60)
        else:
            new_senses = Senses(blindsight=60)

        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Large, rng=rng)

        # constructs with higher CR should have proficiency in STR and CON saves
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR)

        if stats.cr >= 7:
            new_attributes = new_attributes.grant_save_proficiency(Stats.STR, Stats.CON)

        # constructs are heavily armored
        ac_bonus = min(ceil(stats.cr / 5), 3)
        stats = stats.add_ac_template(NaturalArmor, ac_modifier=ac_bonus)

        return stats.copy(
            creature_type=CreatureType.Construct,
            attributes=new_attributes,
            size=size,
            languages=None,
            senses=new_senses,
        )

    def customize_role(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # constructs don't use Light or Medium armor
        stats = stats.remove_ac_templates([MediumArmor, LightArmor])
        return stats


ConstructTemplate: CreatureTypeTemplate = _ConstructTemplate()
