from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_ac_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, speed_modifier=20)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


def as_low_hp_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.8, speed_modifier=20)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Defender)


SkirmisherLowAc = role_variant("Skirmisher.LowAc", MonsterRole.Skirmisher, as_low_ac_skirmisher)
SkirmisherLowHp = role_variant("Skirmisher.LowHp", MonsterRole.Skirmisher, as_low_hp_skirmisher)
Skirmisher = RoleTemplate(
    "Skirmisher", MonsterRole.Skirmisher, [SkirmisherLowAc, SkirmisherLowHp]
)
