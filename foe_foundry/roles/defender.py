from ..ac_templates import HeavyArmor, MediumArmor, NaturalArmor
from ..role_types import MonsterRole
from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Defender(RoleTemplate):
    def __init__(self):
        super().__init__(name="Defender", role=MonsterRole.Defender)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dials = MonsterDials(
            hp_multiplier=0.95,
            attack_damage_multiplier=0.8,
        )

        # defenders have save proficiencies in WIS and CON
        new_attributes = stats.attributes.grant_save_proficiency(Stats.WIS, Stats.CON).boost(
            Stats.STR, 2
        )
        stats = stats.copy(attributes=new_attributes)

        # defenders wear medium or heavy armor if possible, otherwise natural armor
        stats = stats.add_ac_templates([MediumArmor, HeavyArmor, NaturalArmor])

        return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


Defender: RoleTemplate = _Defender()
