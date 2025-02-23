from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..statblocks.base import BaseStatblock


class _HeavyArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Heavy Armor"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost
        ac = 16 + (2 if uses_shield else 0) + quality_level
        return ResolvedArmorClass(
            value=ac,
            armor_type="Heavy Armor" if not uses_shield else "Heavy Armor, Shield",
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac
            + 0.4
            - (1000 if not stats.creature_type.could_wear_heavy_armor else 0),
        )


class _PlateArmor(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Plate Armor"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = max(stats.ac_boost, 0)
        ac = 18 + (2 if uses_shield else 0) + quality_level

        if quality_level > 0:
            text = f"Plate Armor +{quality_level}"
        else:
            text = "Plate Armor"

        return ResolvedArmorClass(
            value=ac,
            armor_type=text,
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.5 - (1000 if stats.attributes.STR < 15 else 0),
        )


class _SplintArmor(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Splint Armor"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = max(stats.ac_boost, 0)
        ac = 17 + (2 if uses_shield else 0) + quality_level

        if quality_level > 0:
            text = f"Splint Armor +{quality_level}"
        else:
            text = "Splint Armor"

        return ResolvedArmorClass(
            value=ac,
            armor_type=text,
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.4 - (1000 if stats.attributes.STR < 15 else 0),
        )


class _ChainmailArmor(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Chainmail"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = max(stats.ac_boost, 0)
        ac = 16 + (2 if uses_shield else 0) + quality_level

        if quality_level > 0:
            text = f"Chainmail +{quality_level}"
        else:
            text = "Chainmail"

        return ResolvedArmorClass(
            value=ac,
            armor_type=text,
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.4 - (1000 if stats.attributes.STR < 13 else 0),
        )


HeavyArmor: ArmorClassTemplate = _HeavyArmorClassTemplate()
PlateArmor: ArmorClassTemplate = _PlateArmor()
SplintArmor: ArmorClassTemplate = _SplintArmor()
ChainmailArmor: ArmorClassTemplate = _ChainmailArmor()
