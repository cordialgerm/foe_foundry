from ...powers import LOW_POWER, MEDIUM_POWER
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _HumanSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Human",
            description="Humans are a diverse species known for their adaptability and ambition",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.cr <= 1:
            modifier = LOW_POWER
        else:
            modifier = MEDIUM_POWER

        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=modifier)
        )
        stats = stats.copy(creature_subtype="Human")
        return stats


HumanSpecies: CreatureSpecies = _HumanSpecies()
