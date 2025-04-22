from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _UnarmoredArmorClassTemplate(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Unarmored"

    @property
    def is_armored(self) -> bool:
        return False

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        # unarmored can't benefit from a positive ac boost
        quality_level = min(stats.ac_boost, 0)

        ac = 10 + min(stats.attributes.stat_mod(Stats.DEX), 5) + quality_level
        return ResolvedArmorClass(
            value=ac,
            armor_type="Unarmored",
            has_shield=uses_shield,
            display_detail=False,
            is_armored=False,
            quality_level=quality_level,
            score=ac,
        )


class _BerserkersDefense(ArmorClassTemplate):
    @property
    def name(self) -> str:
        return "Berserker's Rage"

    @property
    def is_armored(self) -> bool:
        return False

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        ac = (
            10
            + min(stats.attributes.stat_mod(Stats.DEX), 4)
            + min(stats.attributes.stat_mod(Stats.CON), 4)
        )
        return ResolvedArmorClass(
            value=ac,
            armor_type=self.name,
            has_shield=uses_shield,
            is_armored=False,
            display_detail=True,
            quality_level=0,
            score=ac,
        )


Unarmored: ArmorClassTemplate = _UnarmoredArmorClassTemplate()
BerserkersDefense: ArmorClassTemplate = _BerserkersDefense()
