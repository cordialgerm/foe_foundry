from typing import Any

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _UnarmoredArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Unarmored"

    @property
    def can_use_shield(self) -> bool:
        return False

    @property
    def is_armored(self) -> bool:
        return False

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        ac = 10 + min(stats.attributes.stat_mod(Stats.DEX), 5)
        return ResolvedArmorClass(
            value=ac,
            armor_type="Unarmored",
            has_shield=False,
            is_armored=False,
            quality_level=0,  # unarmored doesn't have any modifiers
            score=ac,
        )


Unarmored: ArmorClassTemplate = _UnarmoredArmorClassTemplate()
