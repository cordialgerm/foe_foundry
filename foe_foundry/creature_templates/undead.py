from math import ceil, floor
from typing import Tuple

import numpy as np
from numpy.random import Generator

from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import HeavyArmor, MediumArmor, Unarmored, UnholyArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _UndeadTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Undead", creature_type=CreatureType.Undead)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Skirmisher}:
            options = [
                weapon.Daggers,
                natural.Claw,
                weapon.Shortswords,
                weapon.Shortbow,
                weapon.JavelinAndShield,
            ]
        elif stats.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            options = [
                weapon.Longbow,
                spell.Deathbolt,
                spell.Frostbolt,
                spell.EdlritchBlast,
                spell.Gaze,
            ]
        elif stats.role in {MonsterRole.Bruiser}:
            options = [weapon.Polearm, weapon.Maul, weapon.Greataxe, weapon.Greatsword]
        elif stats.role in {MonsterRole.Defender}:
            options = [
                weapon.MaceAndShield,
                weapon.SpearAndShield,
                weapon.SwordAndShield,
                weapon.RapierAndShield,
            ]
        elif stats.role in {MonsterRole.Leader}:
            options = [weapon.Staff, spell.Deathbolt, weapon.SwordAndShield]
        else:
            raise ValueError(f"Unsupported role {stats.role}")

        index = rng.choice(len(options))
        attack = options[index]

        # Undead do Necrotic or Cold damage if the attack doesn't already have a secondary damage type
        if attack.secondary_damage_type is None:
            secondary_damage_type = choose_enum(
                rng, [DamageType.Necrotic, DamageType.Cold], p=[2, 1]
            )
            stats = stats.copy(secondary_damage_type=secondary_damage_type)

        # Spellcasters use INT
        if attack.attack_type and attack.attack_type.is_spell():
            stats = stats.scale({Stats.INT: Stats.Primary(), Stats.STR: Stats.Scale(7, 1 / 2)})

        return attack, stats

    def customize_attack_template(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # Undead Spellcasters use Unholy armor
        if stats.attack_type.is_spell():
            stats = stats.add_ac_template(UnholyArmor)

        # Undead Defenders and Leaders who fight with weapons use Medium or Heavy armor - "Death Knight"
        if (
            stats.role in {MonsterRole.Defender, MonsterRole.Leader}
            and stats.attack_type == AttackType.MeleeWeapon
        ):
            stats = stats.add_ac_template(MediumArmor)
            if stats.cr >= 7:
                stats = stats.add_ac_template(HeavyArmor)

        return stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # Plants have extremely low mental stats and low Dexterity scores
        stats = stats.scale(
            {
                Stats.STR: Stats.Primary(),
                Stats.DEX: Stats.Scale(8, 1 / 4),
                Stats.INT: Stats.Scale(6, 1 / 6),
                Stats.WIS: Stats.Scale(8, 1 / 6),
                Stats.CHA: Stats.Scale(5, 1 / 6),
            }
        )
        new_attributes = stats.attributes

        # Undead either attack with melee weapons or ranged weapons
        attack_type = choose_enum(rng, [AttackType.MeleeWeapon, AttackType.RangedWeapon])
        damage_type = (
            DamageType.Slashing
            if attack_type == AttackType.MeleeWeapon
            else DamageType.Piercing
        )
        secondary_damage_type = DamageType.Necrotic

        # Immunities
        damage_immunities = stats.damage_immunities.copy() | {DamageType.Poison}
        condition_immunities = stats.condition_immunities.copy() | {
            Condition.Exhaustion,
            Condition.Poisoned,
        }

        # undead are unarmored unless their role grants them armor
        stats = stats.add_ac_template(Unarmored)

        return stats.copy(
            creature_type=CreatureType.Undead,
            size=Size.Medium,
            languages=[],
            senses=stats.senses.copy(darkvision=60),
            attributes=new_attributes,
            primary_damage_type=damage_type,
            secondary_damage_type=secondary_damage_type,
            attack_type=attack_type,
            damage_immunities=damage_immunities,
            condition_immunities=condition_immunities,
        )


UndeadTemplate: CreatureTypeTemplate = _UndeadTemplate()
