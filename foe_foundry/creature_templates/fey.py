from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import LightArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _FeyTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Fey", creature_type=CreatureType.Fey)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        options = {}

        melee_stats = False
        secondar_damage_type = None
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            options = {weapon.Shortbow: 1, weapon.Longbow: 1}
            secondary_damage_type = DamageType.Poison
        elif stats.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            secondary_damage_type = choose_enum(
                rng, [DamageType.Fire, DamageType.Cold, DamageType.Psychic, DamageType.Poison]
            )
            attack = spell.attack_template_for_damage(secondary_damage_type)
            if attack is None:
                raise ValueError(f"Unable to create attack for {secondary_damage_type}")
            options = {attack: 1}
        elif stats.role in {MonsterRole.Defender}:
            options = {
                weapon.SpearAndShield: 1,
                weapon.RapierAndShield: 1,
            }
        elif stats.role in {MonsterRole.Leader}:
            options = {weapon.Whip: 1, weapon.Staff: 1, weapon.RapierAndShield: 1}
        elif stats.role in {MonsterRole.Bruiser}:
            melee_stats = True
            options = {natural.Claw: 1, weapon.Greataxe: 1}

        choices: List[AttackTemplate] = []
        weights = []
        for c, w in options.items():
            choices.append(c)
            weights.append(w)

        weights = np.array(weights) / np.sum(weights)
        indx = rng.choice(len(choices), p=weights)
        choice = choices[indx]

        if melee_stats:
            # melee fey still have good CHA but not as great - instead they get a STR boost
            stats = stats.scale(
                {
                    Stats.STR: Stats.Primary(),
                    Stats.CHA: Stats.CHA.Boost(-2),
                    Stats.DEX: Stats.DEX.Boost(-2),
                }
            )

        if secondar_damage_type:
            stats = stats.copy(secondar_damage_type=secondar_damage_type)

        return choice, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # Fey often have high Charisma and Dexterity scores and moderate-to-high Wisdom scores.
        stats = stats.scale(
            {
                Stats.STR: Stats.Scale(8, 1 / 3),
                Stats.DEX: Stats.Primary(),
                Stats.INT: Stats.Scale(10, 1 / 3),
                Stats.WIS: Stats.Scale(12, 1 / 2),
                Stats.CHA: Stats.Scale(12, 1 / 2),
            }
        )
        new_attributes = stats.attributes

        # Most fey have proficiency in the Deception, Perception, or Persuasion skills.
        skills = choose_enum(
            rng,
            [Skills.Deception, Skills.Persuasion, Skills.Perception],
            size=min(3, ceil(stats.cr / 3)),
        )
        new_attributes = new_attributes.grant_proficiency_or_expertise(*skills)

        # fey are often lightly armored but are dextrous
        stats = stats.add_ac_template(LightArmor)

        return stats.copy(
            creature_type=CreatureType.Fey,
            size=Size.Medium,
            languages=["Common", "Elvish", "Sylvan"],
            senses=stats.senses.copy(darkvision=60),
            attributes=new_attributes,
        )


FeyTemplate: CreatureTypeTemplate = _FeyTemplate()
