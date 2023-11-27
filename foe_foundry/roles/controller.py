from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import ArcaneArmor, Unarmored
from ..attributes import Stats
from ..damage import AttackType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Controller(RoleTemplate):
    def __init__(self):
        super().__init__(name="Controller", role=MonsterRole.Controller)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        # controllers deal less damage but have hard-to-resist abilities
        dials = MonsterDials(attack_damage_multiplier=0.85, difficulty_class_modifier=1)

        # controllers are sharp-witted
        new_attributes = (
            stats.attributes.boost(Stats.INT, 2)
            .boost(Stats.WIS, 2)
            .boost(Stats.CHA, 2)
            .boost(Stats.STR, -2)
            .boost(Stats.DEX, -2)
        )

        # higher-cr controllers have mental save proficiencies
        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(
                Stats.INT, Stats.WIS, Stats.CHA
            )

        stats = stats.apply_monster_dials(dials)
        stats = stats.add_ac_templates([Unarmored, ArcaneArmor])
        stats = stats.copy(
            role=MonsterRole.Controller,
            attack_type=AttackType.RangedSpell,
            attributes=new_attributes,
        )
        return stats


Controller: RoleTemplate = _Controller()
