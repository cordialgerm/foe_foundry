from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hit_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(multiattack_modifier=-1, attack_damage_modifier=2)
    return _as_bruiser(stats, dials)


def as_low_hp_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9, attack_damage_modifier=1)
    return _as_bruiser(stats, dials)


def as_low_ac_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, attack_damage_modifier=1)
    return _as_bruiser(stats, dials)


def _as_bruiser(stats: BaseStatblock, dials: MonsterDials):
    new_attributes = (
        stats.attributes.change_primary(Stats.STR)
        .boost(Stats.INT, -2)
        .boost(Stats.WIS, -2)
        .boost(Stats.CHA, -2)
    )

    if stats.cr >= 4:
        new_attributes = new_attributes.grant_save_proficiency(
            Stats.STR
        ).grant_proficiency_or_expertise(Skills.Athletics)

    # bruisers do not use shields
    new_ac = stats.ac.delta(shield_allowed=False)

    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Bruiser, attributes=new_attributes, ac=new_ac
    )


BruiserLowHit = role_variant("Bruiser.LowHit", MonsterRole.Bruiser, as_low_hit_bruiser)
BruiserLowHp = role_variant("Bruiser.LowHp", MonsterRole.Bruiser, as_low_hp_bruiser)
BruiserLowAc = role_variant("Bruiser.LowAc", MonsterRole.Bruiser, as_low_ac_bruiser)
Bruiser = RoleTemplate(
    "Bruiser", MonsterRole.Bruiser, [BruiserLowHit, BruiserLowHp, BruiserLowAc]
)
