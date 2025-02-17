from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _LightArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Light Armor"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost
        ac = (
            12
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
            score=ac
            + 0.2
            - (1000 if not stats.creature_type.could_wear_light_armor else 0),
        )


LightArmor: ArmorClassTemplate = _LightArmorClassTemplate()
