from math import floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import NaturalArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _ElementalTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Elemental", creature_type=CreatureType.Elemental)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.secondary_damage_type is None:
            raise ValueError("secondary_damage_type is required")

        elemental_attack = spell.attack_template_for_damage(stats.secondary_damage_type)

        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            options = {natural.Slam: 1}
        elif stats.role in {MonsterRole.Leader, MonsterRole.Controller, MonsterRole.Artillery}:
            options = {elemental_attack: 1}
        elif stats.role in {MonsterRole.Bruiser}:
            options = {
                natural.Slam: 2,
                natural.Claw: 1,
                weapon.Greatsword: 1,
                weapon.Greataxe: 1,
            }
        elif stats.role in {MonsterRole.Defender}:
            options = {weapon.SwordAndShield: 1, weapon.MaceAndShield: 1}
        else:
            options = {natural.Slam: 1}

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
        # Elementals generally have strong physical ability scores
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(10, 1 / 3),
                Stats.INT: Stats.Scale(5, 1 / 3),
                Stats.WIS: Stats.Scale(7, 1 / 2),
                Stats.CHA: Stats.Scale(8, 1 / 2),
            }
        )
        new_attributes = stats.attributes

        elemental_type = choose_enum(
            rng,
            [
                DamageType.Fire,
                DamageType.Lightning,
                DamageType.Acid,
                DamageType.Poison,
                DamageType.Cold,
            ],
        )

        stats = stats.grant_resistance_or_immunity(
            resistances={elemental_type},
            immunities={DamageType.Poison} | ({elemental_type} if stats.cr >= 7 else set()),
            nonmagical_resistance=True,
            upgrade_resistance_to_immunity_if_present=True,
            conditions={
                Condition.Poisoned,
                Condition.Exhaustion,
                Condition.Grappled,
                Condition.Paralyzed,
                Condition.Petrified,
                Condition.Prone,
                Condition.Restrained,
            },
        )

        new_senses = stats.senses.copy(darkvision=60)
        size = get_size_for_cr(cr=stats.cr, standard_size=Size.Medium, rng=rng)

        # elementals have natural armor
        stats = stats.add_ac_template(NaturalArmor)

        return stats.copy(
            creature_type=CreatureType.Elemental,
            size=size,
            languages=None,
            senses=new_senses,
            attributes=new_attributes,
            primary_damage_type=elemental_type,
            secondary_damage_type=elemental_type,
        )


ElementalTemplate: CreatureTypeTemplate = _ElementalTemplate()
