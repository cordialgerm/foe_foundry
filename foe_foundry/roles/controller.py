from ..attributes import Stats
from ..damage import AttackType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_default_controller(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_modifier=-1, difficulty_class_modifier=2)

    new_attributes = (
        stats.attributes.boost(Stats.INT, 2)
        .boost(Stats.WIS, 2)
        .boost(Stats.CHA, 2)
        .boost(Stats.STR, -2)
        .boost(Stats.DEX, -2)
    )

    if stats.cr >= 4:
        new_attributes = new_attributes.grant_save_proficiency(Stats.INT, Stats.WIS, Stats.CHA)

    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Controller,
        attack_type=AttackType.RangedSpell,
        attributes=new_attributes,
    )


ControllerDefault = role_variant(
    "Controller.Default", MonsterRole.Controller, as_default_controller
)
Controller = RoleTemplate("Controller", MonsterRole.Controller, [ControllerDefault])
