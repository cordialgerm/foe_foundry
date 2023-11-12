from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import LightArmor, MediumArmor
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Leader(RoleTemplate):
    def __init__(self):
        super().__init__(name="Leader", role=MonsterRole.Leader)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dials = MonsterDials(hp_multiplier=0.8, recommended_powers_modifier=0.5)

        new_attributes = (
            stats.attributes.boost(Stats.INT, 4)
            .boost(Stats.WIS, 2)
            .grant_proficiency_or_expertise(Skills.Persuasion)
        )

        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(Stats.INT, Stats.WIS)

        # leaders wear light or medium armor
        stats = stats.add_ac_templates([LightArmor, MediumArmor])

        return stats.apply_monster_dials(dials).copy(
            role=MonsterRole.Leader,
            attributes=new_attributes,
        )


Leader: RoleTemplate = _Leader()
