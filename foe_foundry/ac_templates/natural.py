from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..size import Size
from ..statblocks.base import BaseStatblock


class _NaturalArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Natural Armor"

    @property
    def is_armored(self) -> bool:
        return False

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = stats.ac_boost

        if stats.size >= Size.Huge:
            max_con = 4
        elif stats.size >= Size.Large:
            max_con = 3
        else:
            max_con = 2

        ac = (
            10
            + max(0, min(stats.attributes.stat_mod(Stats.DEX), 3))
            + min(stats.attributes.stat_mod(Stats.CON), max_con)
        ) + quality_level

        return ResolvedArmorClass(
            value=ac,
            armor_type="Natural Armor",
            has_shield=uses_shield,
            is_armored=False,
            quality_level=quality_level,
            score=ac + 0.1,
        )


NaturalArmor: ArmorClassTemplate = _NaturalArmorClassTemplate()
