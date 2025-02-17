from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _MediumArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Medium Armor"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost
        ac = (
            13
            + max(0, min(stats.attributes.stat_mod(Stats.DEX), 2))
            + quality_level
            + (2 if uses_shield else 0)
        )
        return ResolvedArmorClass(
            value=ac,
            armor_type="Medium Armor" if not uses_shield else "Medium Armor, Shield",
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac
            + 0.3
            - (1000 if not stats.creature_type.could_wear_heavy_armor else 0),
        )


MediumArmor: ArmorClassTemplate = _MediumArmorClassTemplate()
