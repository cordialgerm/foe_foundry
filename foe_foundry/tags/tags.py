from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from foe_foundry.creature_types import CreatureType
from foe_foundry.damage import DamageType
from foe_foundry.environs import Biome, Development, ExtraplanarInfluence, Region, Terrain
from foe_foundry.features import ActionType
from foe_foundry.power_types import PowerType
from foe_foundry.role_types import MonsterRole
from foe_foundry.size import Size
from .definitions import TagDefinition, get_tag_definition


@dataclass(frozen=True)
class MonsterTag:
    tag: str
    tag_type: str
    
    @property
    def definition(self) -> Optional[TagDefinition]:
        """Get the full tag definition with description and icon"""
        return get_tag_definition(self.tag.lower().replace(" ", "_"))
    
    @property
    def description(self) -> str:
        """Get the tag description"""
        if self.definition:
            return self.definition.description
        return f"Tag: {self.tag}"
    
    @property
    def icon(self) -> Optional[str]:
        """Get the tag icon filename"""
        if self.definition:
            return self.definition.icon
        return None

    @property
    def color(self) -> str:
        """Get the tag color"""
        if self.definition:
            return self.definition.color
        return "#6B7280"  # Default gray color

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
    def from_biome(biome: Biome) -> MonsterTag:
        return MonsterTag(tag=biome.name, tag_type="biome")

    @staticmethod
    def from_terrain(terrain: Terrain) -> MonsterTag:
        return MonsterTag(tag=terrain.name, tag_type="terrain")

    @staticmethod
    def from_development(development: Development) -> MonsterTag:
        return MonsterTag(tag=development.name, tag_type="development")

    @staticmethod
    def from_extraplanar(extraplanar: ExtraplanarInfluence) -> MonsterTag:
        return MonsterTag(tag=extraplanar.name, tag_type="extraplanar")

    @staticmethod
    def from_region(region: Region) -> MonsterTag:
        return MonsterTag(tag=region.name, tag_type="region")

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
            return MonsterTag(tag="tier0", tag_type="cr_tier")
        elif cr < 4:
            return MonsterTag(tag="tier1", tag_type="cr_tier")
        elif cr < 13:
            return MonsterTag(tag="tier2", tag_type="cr_tier")
        elif cr < 20:
            return MonsterTag(tag="tier3", tag_type="cr_tier")
        else:
            return MonsterTag(tag="tier4", tag_type="cr_tier")

    @staticmethod
    def from_family(family: str) -> MonsterTag:
        return MonsterTag(tag=family, tag_type="monster_family")

    @staticmethod
    def from_theme(theme: str) -> MonsterTag:
        return MonsterTag(tag=theme, tag_type="theme")

    @staticmethod
    def from_power_type(power_type: PowerType) -> MonsterTag:
        return MonsterTag(tag=power_type.name, tag_type="power_type")

    @staticmethod
    def from_size(size: Size) -> MonsterTag:
        return MonsterTag(tag=size.name, tag_type="size")
