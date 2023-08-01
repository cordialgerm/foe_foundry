from ..attributes import Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hp_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2)
    return _as_ambusher(stats, dials)


def as_low_ac_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9)
    return _as_ambusher(stats, dials)


def _as_ambusher(stats: BaseStatblock, dials: MonsterDials) -> BaseStatblock:
    dials.primary_attribute = Stats.DEX
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Ambusher)


AmbusherLowHp = role_variant(
    name="Ambusher.LowHp", role=MonsterRole.Ambusher, apply=as_low_hp_ambusher
)
AmbusherLowAc = role_variant(
    name="Ambusher.LowAc", role=MonsterRole.Ambusher, apply=as_low_ac_ambusher
)
Ambusher = RoleTemplate(
    name="Ambusher", role=MonsterRole.Ambusher, variants=[AmbusherLowHp, AmbusherLowAc]
)
