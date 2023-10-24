from ..ac_templates import LightArmor
from ..attributes import Skills, Stats
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate, role_variant


def as_low_ac_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(ac_modifier=-2, speed_modifier=20)
    return _as_skirmisher(stats, dials)


def as_low_hp_skirmisher(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(hp_multiplier=0.9, speed_modifier=20)
    return _as_skirmisher(stats, dials)


def _as_skirmisher(stats: BaseStatblock, dials: MonsterDials) -> BaseStatblock:
    new_attributes = stats.attributes.boost(Stats.DEX, 4)

    if stats.cr >= 4:
        new_attributes = new_attributes.grant_save_proficiency(
            Stats.DEX
        ).grant_proficiency_or_expertise(Skills.Acrobatics)

    # skirmishers wear light armor
    stats = stats.add_ac_template(LightArmor)

    return stats.apply_monster_dials(dials).copy(
        role=MonsterRole.Skirmisher,
        attributes=new_attributes,
    )


SkirmisherLowAc = role_variant("Skirmisher.LowAc", MonsterRole.Skirmisher, as_low_ac_skirmisher)
SkirmisherLowHp = role_variant("Skirmisher.LowHp", MonsterRole.Skirmisher, as_low_hp_skirmisher)
Skirmisher = RoleTemplate(
    "Skirmisher", MonsterRole.Skirmisher, [SkirmisherLowAc, SkirmisherLowHp]
)
