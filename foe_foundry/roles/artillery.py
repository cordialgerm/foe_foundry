from foe_foundry.statblocks import BaseStatblock

from ..ac_templates import LightArmor, Unarmored
from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import RoleTemplate


class _Artillery(RoleTemplate):
    def __init__(self):
        super().__init__(name="Artillery", role=MonsterRole.Artillery)

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dials = MonsterDials(attack_damage_multiplier=1.05, hp_multiplier=0.9)

        new_attack_type = (
            AttackType.RangedWeapon
            if stats.creature_type in {CreatureType.Humanoid, CreatureType.Beast}
            else AttackType.RangedSpell
        )

        new_attributes = stats.attributes.boost(Stats.INT, 2).boost(Stats.DEX, 2)

        if stats.cr >= 4:
            new_attributes = new_attributes.grant_save_proficiency(
                Stats.INT
            ).grant_proficiency_or_expertise(Skills.Perception, Skills.Investigation)

        changes: dict = dict(
            role=MonsterRole.Artillery,
            attack_type=new_attack_type,
            attributes=new_attributes,
        )

        if (
            new_attack_type == AttackType.RangedSpell
            and stats.secondary_damage_type is not None
        ):
            # if the monster has a secondary damage type, then prefer that for the ranged spell damage
            changes.update(primary_damage_type=stats.secondary_damage_type)

        stats = stats.apply_monster_dials(dials)
        stats = stats.add_ac_templates([LightArmor, Unarmored])
        stats = stats.copy(**changes)
        return stats


Artillery: RoleTemplate = _Artillery()
