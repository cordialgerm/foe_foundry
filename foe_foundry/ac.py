from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, auto

from .creature_types import CreatureType


class ArmorType(StrEnum):
    Unarmored = auto()
    Light = auto()
    Medium = auto()
    Heavy = auto()
    Natural = auto()
    Arcane = auto()
    Divine = auto()

    def increment(self) -> ArmorType:
        if self == ArmorType.Unarmored:
            return ArmorType.Light
        elif self == ArmorType.Light:
            return ArmorType.Medium
        elif self == ArmorType.Medium:
            return ArmorType.Heavy
        else:
            return self

    def decrement(self) -> ArmorType:
        if self == ArmorType.Light:
            return ArmorType.Unarmored
        elif self == ArmorType.Medium:
            return ArmorType.Light
        elif self == ArmorType.Heavy:
            return ArmorType.Medium
        else:
            return self


@dataclass
class ArmorClass:
    value: int
    armor_type: ArmorType
    quality: int = 0
    has_shield: bool = False
    dex_mod: int = 0
    spellcasting_mod: int = 0

    def __post_init__(self):
        armor_description = _describe_armor(self.armor_type, self.quality)
        if self.has_shield:
            armor_description += ", Shield"
        self.description = f"{self.value} ({armor_description})"

    def __repr__(self) -> str:
        return self.description

    @staticmethod
    def default(value: int) -> ArmorClass:
        return ArmorClass(
            value=value, armor_type=ArmorType.Natural, quality=0, has_shield=False
        )

    def delta(
        self,
        change: int = 0,
        armor_type: ArmorType | None = None,
        dex: int | None = None,
        spellcasting: int | None = None,
        shield_allowed: bool = False,
    ) -> ArmorClass:
        new_target = self.value + change
        if self.has_shield and not shield_allowed:
            new_target -= 2
        elif not self.has_shield and shield_allowed:
            new_target += 2

        if armor_type is not None:
            new_armor_type = armor_type
        elif change == 0:
            new_armor_type = self.armor_type
        elif change < 0:
            new_armor_type = self.armor_type.decrement()
        else:
            new_armor_type = self.armor_type.increment()

        return ArmorClass.reasonable_ac(
            target_ac=new_target,
            armor_type=new_armor_type,
            has_shield=shield_allowed,
            dex=dex or self.dex_mod,
            spellcasting=spellcasting or self.spellcasting_mod,
        )

    @staticmethod
    def reasonable_ac(
        target_ac: int,
        armor_type: ArmorType,
        dex: int = 0,
        spellcasting: int = 0,
        has_shield: bool = False,
    ) -> ArmorClass:
        max_quality = 2
        args = dict(dex_mod=dex, spellcasting_mod=spellcasting)

        if armor_type == ArmorType.Unarmored:
            unarmored_ac = 10 + dex
            proposed_ac = max(target_ac, unarmored_ac)
            max_allowed_ac = unarmored_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_ac)
            quality = new_ac - unarmored_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Unarmored,
                quality=quality,
                has_shield=False,
                **args,
            )
        elif armor_type == ArmorType.Arcane:
            mage_ac = 10 + dex + spellcasting
            proposed_ac = max(target_ac, mage_ac)
            max_allowed_ac = mage_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_ac)
            quality = new_ac - mage_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Arcane,
                quality=quality,
                has_shield=False,
                **args,
            )
        elif armor_type == ArmorType.Divine:
            divine_ac = 10 + dex + spellcasting + (2 if has_shield else 0)
            proposed_ac = max(target_ac, divine_ac)
            max_allowed_divine_ac = divine_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_divine_ac)
            quality = new_ac - divine_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Divine,
                quality=quality,
                has_shield=has_shield,
                **args,
            )
        elif armor_type == ArmorType.Natural:
            return ArmorClass(value=target_ac, armor_type=ArmorType.Natural)
        elif armor_type == ArmorType.Light:
            leather_ac = 11 + dex + (2 if has_shield else 0)
            proposed_ac = max(target_ac, leather_ac)
            max_allowed_light_ac = leather_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_light_ac)
            quality = new_ac - leather_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Light,
                quality=quality,
                has_shield=has_shield,
                **args,
            )
        elif armor_type == ArmorType.Medium:
            max_dex = min(dex, 2)
            scale_ac = 14 + max_dex
            proposed_ac = max(target_ac, scale_ac)
            max_allowed_medium_ac = scale_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_medium_ac)
            quality = new_ac - scale_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Medium,
                quality=quality,
                has_shield=has_shield,
                **args,
            )
        elif armor_type == ArmorType.Heavy:
            chain_ac = 16 + (2 if has_shield else 0)
            proposed_ac = max(target_ac, chain_ac)
            max_allowed_heavy_ac = chain_ac + max_quality
            new_ac = min(proposed_ac, max_allowed_heavy_ac)
            quality = new_ac - chain_ac
            return ArmorClass(
                value=new_ac,
                armor_type=ArmorType.Heavy,
                quality=quality,
                has_shield=has_shield,
                **args,
            )
        else:
            raise ValueError("Unsupported ArmorTye")

    @staticmethod
    def could_use_shield_or_wear_armor(creature_type: CreatureType) -> bool:
        return creature_type in {
            CreatureType.Celestial,
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
        }


def _describe_armor(armor_type: ArmorType, quality: int) -> str:
    if armor_type == ArmorType.Unarmored:
        return "Unarmored"
    elif armor_type == ArmorType.Natural:
        return "Natural Armor"
    elif armor_type == ArmorType.Arcane:
        return "Mage Armor"
    elif armor_type == ArmorType.Divine:
        return "Divine Blessing"
    elif armor_type == ArmorType.Light:
        if quality < 0:
            return "Padded Armor"
        elif quality == 0:
            return "Leather"
        else:
            return "Studded Leather"
    elif armor_type == ArmorType.Medium:
        if quality <= -2:
            return "Hide"
        elif quality == -1:
            return "Chain Shirt"
        elif quality == 0:
            return "Scale Mail"
        elif quality == 1:
            return "Breastplate"
        else:
            return "Half Plate"
    elif armor_type == ArmorType.Heavy:
        if quality <= -1:
            return "Ring Mail"
        elif quality == 0:
            return "Chain Mail"
        elif quality == 1:
            return "Splint"
        else:
            return "Plate"
    else:
        raise ValueError("Unsupported ArmorTye")
