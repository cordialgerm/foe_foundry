from math import ceil, floor
from typing import Tuple

import numpy as np
from numpy.random import Generator

from ..ac_templates import HideArmor
from ..attack_template import AttackTemplate, natural, spell, weapon
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from ..utils.rng import choose_options
from .template import CreatureTypeTemplate


class _HumanoidTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Humanoid", creature_type=CreatureType.Humanoid)

    def select_attack_template(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[AttackTemplate, BaseStatblock]:
        # secondary damage type possibilities for humanoids
        dmg_types = {
            DamageType.Bludgeoning: 4.0,  # sentinel value - no special damage
            DamageType.Radiant: 2.0,
            DamageType.Cold: 1.0,
            DamageType.Fire: 1.0,
            DamageType.Necrotic: 2.0,
            DamageType.Poison: 2.0,
        }

        if stats.role in {MonsterRole.Ambusher}:
            attacks = [weapon.Shortbow, weapon.Daggers, weapon.Shortswords]
            dmg_types = [DamageType.Bludgeoning, DamageType.Poison]
        elif stats.role in {MonsterRole.Skirmisher}:
            attacks = [
                weapon.JavelinAndShield,
                weapon.Shortbow,
                weapon.RapierAndShield,
                weapon.Shortswords,
            ]
            dmg_types = [DamageType.Bludgeoning, DamageType.Poison]
        elif stats.role in {MonsterRole.Artillery}:
            attacks = [
                weapon.Longbow,
                weapon.Crossbow,
                spell.Firebolt,
                spell.HolyBolt,
                spell.Shock,
            ]
        elif stats.role in {MonsterRole.Controller}:
            attacks = [
                spell.ArcaneBurst,
                spell.EdlritchBlast,
                spell.Frostbolt,
                spell.Shock,
                natural.Slam,
                spell.Acidsplash,
                spell.Deathbolt,
                spell.Frostbolt,
                spell.Shock,
                spell.Thundrousblast,
            ]
        elif stats.role in {MonsterRole.Bruiser}:
            attacks = [
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.Maul,
                weapon.Polearm,
                natural.Slam,
            ]
        elif stats.role in {MonsterRole.Defender}:
            attacks = [weapon.SpearAndShield, weapon.SwordAndShield, weapon.MaceAndShield]
        elif stats.role in {MonsterRole.Leader}:
            attacks = [weapon.SwordAndShield, weapon.Greatsword, weapon.Staff, weapon.Whip]
        else:
            raise RuntimeError("Unexpected error")

        attack = choose_options(rng, attacks)
        damage_type = choose_options(rng, dmg_types)
        if damage_type == DamageType.Bludgeoning:
            damage_type = None  # this was the sentinel value to ignore

        secondary_damage_type = attack.secondary_damage_type or damage_type

        # no magical infusion for fists...
        if attack == natural.Slam:
            secondary_damage_type = None

        stats = stats.copy(secondary_damage_type=secondary_damage_type)
        return attack, stats

    def alter_base_stats(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        stats = stats.apply_monster_dials(MonsterDials(recommended_powers_modifier=1))

        return stats.copy(
            creature_type=CreatureType.Humanoid, size=Size.Medium, languages=["Common"]
        )

    def customize_role(self, stats: BaseStatblock, rng: Generator) -> BaseStatblock:
        # humanoid stats are based on their role
        if stats.role in {MonsterRole.Ambusher, MonsterRole.Artillery, MonsterRole.Skirmisher}:
            # ambushers, artillery, and skirmishers are dex-based
            # mental stats are semi-randomized
            mental_stats: list = [
                Stats.Scale(8, 1 / 4),
                Stats.Scale(8, 1 / 3),
            ]
            rng.shuffle(mental_stats)

            stats = stats.scale(
                {
                    Stats.DEX: Stats.Primary(),
                    Stats.STR: Stats.Scale(10, 1 / 2),
                    Stats.WIS: Stats.Scale(10, 1 / 2),
                    Stats.INT: mental_stats[0],
                    Stats.CHA: mental_stats[1],
                }
            )
        elif stats.role == MonsterRole.Leader:
            # leaders are persuasive and overall good combatants
            stats = stats.scale(
                {
                    Stats.CHA: Stats.Primary(),
                    Stats.DEX: Stats.Scale(10, 1 / 4),
                    Stats.WIS: Stats.Scale(10, 1 / 3),
                    Stats.INT: Stats.Scale(10, 1 / 2),
                    Stats.STR: Stats.Scale(10, 1 / 2),
                }
            )
        elif stats.role == MonsterRole.Controller:
            # controllers focus on intelligence
            stats = stats.scale(
                {
                    Stats.INT: Stats.Primary(),
                    Stats.DEX: Stats.Scale(10, 1 / 4),
                    Stats.WIS: Stats.Scale(10, 1 / 3),
                    Stats.CHA: Stats.Scale(8, 1 / 4),
                    Stats.STR: Stats.Scale(8, 1 / 6),
                }
            )
        elif stats.role in {MonsterRole.Defender, MonsterRole.Bruiser}:
            # phyiscal combatants focus on strength
            # mental stats are semi-randomized
            mental_stats: list = [
                Stats.Scale(8, 1 / 4),
                Stats.Scale(8, 1 / 3),
                Stats.Scale(8, 1 / 2),
            ]
            rng.shuffle(mental_stats)

            stats = stats.scale(
                {
                    Stats.STR: Stats.Primary(),
                    Stats.DEX: Stats.Scale(8, 1 / 3),
                    Stats.INT: mental_stats[0],
                    Stats.WIS: mental_stats[1],
                    Stats.CHA: mental_stats[2],
                }
            )

            # humanoid bruisers wear Hide armor instead of natural armor
            stats = stats.add_ac_template(HideArmor)

        return stats


HumanoidTemplate: CreatureTypeTemplate = _HumanoidTemplate()
