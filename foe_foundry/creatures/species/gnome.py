from ...attributes import AbilityScore, Skills
from ...powers import RIBBON_POWER
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _GnomeSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Gnome",
            description="Gnomes are a small, clever species known for their intelligence and curiosity",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().alter_base_stats(stats)
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.copy(creature_subtype="Gnome", size=Size.Small)
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana)
        stats = stats.scale(
            {
                AbilityScore.INT: AbilityScore.INT.Boost(2),
                AbilityScore.WIS: AbilityScore.WIS.Boost(2),
            }
        )
        stats = stats.with_roles(additional_roles=[MonsterRole.Controller])
        return stats


GnomeSpecies: CreatureSpecies = _GnomeSpecies()
