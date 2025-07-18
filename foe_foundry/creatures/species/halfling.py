from ...attributes import AbilityScore, Skills
from ...powers import RIBBON_POWER
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _HalflingSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Halfling",
            description="Halflings are a small, nimble species known for their luck and stealth",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().alter_base_stats(stats)
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.copy(creature_subtype="Halfling", size=Size.Small)
        stats = stats.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.scale(
            {
                AbilityScore.DEX: AbilityScore.DEX.Boost(2),
                AbilityScore.WIS: AbilityScore.WIS.Boost(2),
            }
        )
        stats = stats.with_roles(additional_roles=[MonsterRole.Skirmisher])
        return stats


HalflingSpecies: CreatureSpecies = _HalflingSpecies()
