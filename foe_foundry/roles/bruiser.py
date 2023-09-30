from ..ac_templates import NaturalArmor, Unarmored
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from .template import RoleTemplate, role_variant


def as_bruiser(stats: BaseStatblock) -> BaseStatblock:
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

    stats = stats.add_ac_templates([Unarmored, NaturalArmor])
    stats = stats.copy(role=MonsterRole.Bruiser, attributes=new_attributes)
    return stats


BruiserLowAc = role_variant("Bruiser.LowAc", MonsterRole.Bruiser, as_bruiser)
Bruiser = RoleTemplate("Bruiser", MonsterRole.Bruiser, [BruiserLowAc])
