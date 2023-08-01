from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_ac_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2)
    return _as_ambusher(stats, dials)


def as_low_hp_ambusher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9)
    return _as_ambusher(stats, dials)


def _as_ambusher(stats: BaseStatblock, dials: MonsterDials) -> BaseStatblock:
    new_attributes = stats.attributes.change_primary(Stats.DEX)

    if stats.cr >= 4:
        new_attributes = new_attributes.grant_save_proficiency(
            Stats.DEX
        ).grant_proficiency_or_expertise(Skills.Stealth)

    # ambushers do not use shields
    new_ac = stats.ac.delta(shield_allowed=False, dex=new_attributes.stat_mod(Stats.DEX))

    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Ambusher, attributes=new_attributes, ac=new_ac
    )


AmbusherLowHp = role_variant(
    name="Ambusher.LowHp", role=MonsterRole.Ambusher, apply=as_low_hp_ambusher
)
AmbusherLowAc = role_variant(
    name="Ambusher.LowAc", role=MonsterRole.Ambusher, apply=as_low_ac_ambusher
)
Ambusher = RoleTemplate(
    name="Ambusher", role=MonsterRole.Ambusher, variants=[AmbusherLowHp, AmbusherLowAc]
)
