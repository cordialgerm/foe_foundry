from __future__ import annotations

from dataclasses import dataclass

from foe_foundry.creature_types import CreatureType
from foe_foundry.damage import DamageType
from foe_foundry.environs import MonsterEnviron
from foe_foundry.features import ActionType
from foe_foundry.power_types import PowerType
from foe_foundry.role_types import MonsterRole


@dataclass(frozen=True)
class MonsterTag:
    tag: str
    tag_type: str

    @staticmethod
    def from_creature_type(ct: CreatureType) -> MonsterTag:
        return MonsterTag(tag=ct.name, tag_type="creature_type")

    @staticmethod
    def from_role(role: MonsterRole) -> MonsterTag:
        return MonsterTag(tag=role.name, tag_type="monster_role")

    @staticmethod
    def legendary() -> MonsterTag:
        return MonsterTag(tag="Legendary", tag_type="monster_role")

    @staticmethod
    def from_environ(environ: MonsterEnviron) -> MonsterTag:
        return MonsterTag(tag=environ.name, tag_type="environ")

    @staticmethod
    def from_action_type(action_type: ActionType) -> MonsterTag:
        return MonsterTag(tag=action_type.name, tag_type="action_type")

    @staticmethod
    def from_damage_type(damage_type: DamageType) -> MonsterTag:
        return MonsterTag(tag=damage_type.name, tag_type="damage_type")

    @staticmethod
    def from_cr(cr: float) -> MonsterTag:
        # Tier 0 is level 1 -> CR 0, 1/8, 1/4, 1/2
        # Tier 1 is level 2-4 -> CR 1 - 3
        # Tier 2 is level 5-9 -> CR 4 - 12
        # Tier 3 is level 10-14 -> CR 13 - 19
        # Tier 4 is level 15-20 -> CR 20+

        if cr < 1:
            return MonsterTag(tag="Tier 0", tag_type="tier")
        elif cr < 4:
            return MonsterTag(tag="Tier 1", tag_type="tier")
        elif cr < 13:
            return MonsterTag(tag="Tier 2", tag_type="tier")
        elif cr < 20:
            return MonsterTag(tag="Tier 3", tag_type="tier")
        else:
            return MonsterTag(tag="Tier 4", tag_type="tier")

    @staticmethod
    def from_family(family: str) -> MonsterTag:
        return MonsterTag(tag=family, tag_type="monster_family")

    @staticmethod
    def from_theme(theme: str) -> MonsterTag:
        return MonsterTag(tag=theme, tag_type="theme")

    @staticmethod
    def from_power_type(power_type: PowerType) -> MonsterTag:
        return MonsterTag(tag=power_type.name, tag_type="power_type")
