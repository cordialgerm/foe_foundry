from typing import Any

from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _ArcaneArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Arcane Armor"

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
        quality_level = stats.ac_boost

        ac1 = 13 + min(stats.attributes.stat_mod(Stats.DEX), 5)
        ac2 = (
            10
            + max(0, min(stats.attributes.stat_mod(Stats.DEX), 2))
            + min(stats.attributes.stat_mod(Stats.INT), 4)
        )
        ac = max(ac1, ac2) + quality_level

        return ResolvedArmorClass(
            value=ac,
            armor_type="Arcane Armor",
            has_shield=False,
            is_armored=False,
            quality_level=quality_level,
            score=ac
            + 0.7
            - (1000 if not stats.attributes.is_sapient else 0)
            - (1000 if not stats.attack_type.is_spell() else 0),
        )


ArcaneArmor: ArmorClassTemplate = _ArcaneArmorClassTemplate()
