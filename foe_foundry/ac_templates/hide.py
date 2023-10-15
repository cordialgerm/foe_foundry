from typing import Any

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _HideArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Hide"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost
        ac = 13 + max(0, min(stats.attributes.stat_mod(Stats.DEX), 2)) + quality_level
        return ResolvedArmorClass(
            value=ac,
            armor_type="Hide",
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.2 - (1000 if not stats.creature_type.could_wear_armor else 0),
        )


HideArmor: ArmorClassTemplate = _HideArmorClassTemplate()
