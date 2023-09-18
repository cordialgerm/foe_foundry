from math import ceil, floor

from numpy.random import Generator

from foe_foundry.statblocks import BaseStatblock

from ..ac import ArmorType
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size, get_size_for_cr
from ..statblocks import BaseStatblock, MonsterDials
from ..utils.rng import choose_enum
from .template import CreatureTypeTemplate


class _HumanoidTemplate(CreatureTypeTemplate):
    def __init__(self):
        super().__init__(name="Humanoid", creature_type=CreatureType.Humanoid)

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

        return stats


HumanoidTemplate: CreatureTypeTemplate = _HumanoidTemplate()
