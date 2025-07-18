from ...attributes import AbilityScore
from ...powers import RIBBON_POWER
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _OrcSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Orc",
            description="Orcs are a powerful and aggressive species that are known for their endurance and strength",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().alter_base_stats(stats)
        stats = stats.apply_monster_dials(
            MonsterDials(
                ac_modifier=-1,
                recommended_powers_modifier=-RIBBON_POWER,
                attack_damage_multiplier=1.1,
            )
        )
        stats = stats.copy(creature_subtype="Orc")
        stats = stats.change_abilities({AbilityScore.STR: 2})
        stats = stats.with_roles(additional_roles=[MonsterRole.Bruiser])
        return stats


OrcSpecies: CreatureSpecies = _OrcSpecies()
