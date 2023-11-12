from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import LightArmor, Unarmored
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Ambusher(RoleTemplate):
    def __init__(self):
        super().__init__(name="Ambusher", role=MonsterRole.Ambusher)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dials = MonsterDials(hp_multiplier=0.9)
        new_attributes = stats.attributes.change_primary(Stats.DEX)

        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(
                Stats.DEX
            ).grant_proficiency_or_expertise(Skills.Stealth)

        stats = stats.apply_monster_dials(dials)
        stats = stats.add_ac_templates([LightArmor, Unarmored])
        stats = stats.copy(
            role=MonsterRole.Ambusher,
            attributes=new_attributes,
        )
        return stats


Ambusher: RoleTemplate = _Ambusher()
