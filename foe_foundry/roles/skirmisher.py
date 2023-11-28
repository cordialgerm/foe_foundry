from ..ac_templates import LightArmor
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Skirmisher(RoleTemplate):
    def __init__(self):
        super().__init__(name="Skirmisher", role=MonsterRole.Skirmisher)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dials = MonsterDials(hp_multiplier=0.9, speed_modifier=20)
        new_attributes = stats.attributes.boost(Stats.DEX, 4)

        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(
                Stats.DEX
            ).grant_proficiency_or_expertise(Skills.Acrobatics)

        # skirmishers wear light armor
        stats = stats.add_ac_template(LightArmor)

        return stats.apply_monster_dials(dials).copy(
            role=MonsterRole.Skirmisher,
            attributes=new_attributes,
        )


Skirmisher: RoleTemplate = _Skirmisher()
