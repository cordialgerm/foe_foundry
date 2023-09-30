from typing import Any

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _LightArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Light Armor"

    @property
    def can_use_shield(self) -> bool:
        return True

    @property
    def is_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost
        ac = (
            10
            + min(stats.attributes.stat_mod(Stats.DEX), 5)
            + quality_level
            + (2 if uses_shield else 0)
        )
        return ResolvedArmorClass(
            value=ac,
            armor_type="Light Armor" if not uses_shield else "Light Armor, Shield",
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.2 - (1000 if not stats.creature_type.could_wear_armor else 0),
        )


LightArmor: ArmorClassTemplate = _LightArmorClassTemplate()
