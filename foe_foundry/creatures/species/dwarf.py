from ...damage import DamageType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _DwarfSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Dwarf",
            description="Dwarves were raised from the earth in the elder days by a deity of the forge. They are known for their hardiness, craftsmanship, their love of stone and metal, and their fierce loyalty to their clans.",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().alter_base_stats(stats)
        stats = stats.grant_resistance_or_immunity(resistances={DamageType.Poison})
        stats = stats.apply_monster_dials(MonsterDials(hp_multiplier=1.1))
        stats = stats.with_roles(additional_roles=[MonsterRole.Soldier])
        stats = stats.copy(creature_subtype="Dwarf")
        return stats


DwarfSpecies: CreatureSpecies = _DwarfSpecies()
