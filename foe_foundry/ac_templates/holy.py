from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _HolyArmorClassTemplate(ArmorClassTemplate):
    def __init__(self, is_holy: bool = True):
        self.is_holy = is_holy

    @property
    def name(self) -> str:
        return "Holy Armor" if self.is_holy else "Unholy Armor"

    @property
    def is_armored(self) -> bool:
        return False

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost

        dex_mod = max(0, min(stats.attributes.stat_mod(Stats.DEX), 2))
        con_mod = max(0, min(stats.attributes.stat_mod(Stats.CON), 2))

        ac = (
            10
            + max(dex_mod, con_mod)
            + max(0, min(stats.attributes.spellcasting_mod, 4))
            + (2 if uses_shield else 0)
            + quality_level
        )

        return ResolvedArmorClass(
            value=ac,
            armor_type=self.name if not uses_shield else f"{self.name}, Shield",
            has_shield=uses_shield,
            is_armored=False,
            quality_level=quality_level,
            display_detail=True,
            score=ac + 0.6 - (1000 if not stats.attributes.is_sapient else 0),
        )


HolyArmor: ArmorClassTemplate = _HolyArmorClassTemplate(is_holy=True)
UnholyArmor: ArmorClassTemplate = _HolyArmorClassTemplate(is_holy=False)
