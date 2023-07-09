from ..damage import AttackType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_default_controller(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_damage_modifier=-1, difficulty_class_modifier=2)
    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Controller, attack_type=AttackType.RangedSpell
    )


ControllerDefault = role_variant(
    "Controller.Default", MonsterRole.Controller, as_default_controller
)
Controller = RoleTemplate("Controller", MonsterRole.Controller, [ControllerDefault])
