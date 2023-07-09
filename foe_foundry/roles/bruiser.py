from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_hit_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=-2, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


def as_low_hp_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9, attack_hit_modifier=-1, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


def as_low_ac_bruiser(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, attack_damage_modifier=2)
    return stats.apply_monster_dials(dials).copy(role=MonsterRole.Bruiser)


BruiserLowHit = role_variant("Bruiser.LowHit", MonsterRole.Bruiser, as_low_hit_bruiser)
BruiserLowHp = role_variant("Bruiser.LowHp", MonsterRole.Bruiser, as_low_hp_bruiser)
BruiserLowAc = role_variant("Bruiser.LowAc", MonsterRole.Bruiser, as_low_ac_bruiser)
Bruiser = RoleTemplate(
    "Bruiser", MonsterRole.Bruiser, [BruiserLowHit, BruiserLowHp, BruiserLowAc]
)
