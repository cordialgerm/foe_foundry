from typing import Any

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
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
            score=ac + 0.4 - (1000 if not stats.creature_type.could_wear_heavy_armor else 0),
        )


HeavyArmor: ArmorClassTemplate = _HeavyArmorClassTemplate()
